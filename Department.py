import streamlit as st
import pandas as pd
import pyodbc
import math


# =====================================================
# HELPER: COLUMN EXISTS
# =====================================================
def column_exists(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
        """,
        table_name,
        column_name
    )
    return cursor.fetchone()[0] > 0


# =====================================================
# SESSION STATE
# =====================================================
if "selected_department" not in st.session_state:
    st.session_state.selected_department = "Process"

if "last_project_id" not in st.session_state:
    st.session_state.last_project_id = None


# =====================================================
# SAFE HELPERS
# =====================================================
def safe_float(value):
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    try:
        return float(value)
    except:
        return None


def safe_str(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return str(value).strip()


# =====================================================
# DASHBOARD
# =====================================================
def equipment_dashboard():

    # ✅ LOCK PAGE HERE (NO NAV CHANGE ALLOWED)
    st.session_state.current_page = "Dashboard"

    # Reset department on project change
    if st.session_state.last_project_id != st.session_state.project_id:
        st.session_state.selected_department = "Process"
        st.session_state.last_project_id = st.session_state.project_id

    st.markdown(f"## 📌 Current Project: {st.session_state.project_name}")
    st.divider()

    departments = ["Process", "Electrical", "Static", "Rotary", "Structural", "HSE"]

    selected_department = st.radio(
        "Select Department",
        departments,
        index=departments.index(st.session_state.selected_department),
        horizontal=True,
        key=f"dept_{st.session_state.project_id}"
    )
    st.session_state.selected_department = selected_department

    table_map = {
        "Process": "process_equipments",
        "Electrical": "electrical_equipments",
        "Static": "static_equipments",
        "Rotary": "rotary_equipments",
        "Structural": "structural_equipments",
        "HSE": "hse_equipments",
    }

    table_name = table_map[selected_department]

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\MSSQLSERVER01;"
        "DATABASE=Cost_Estimation;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()

    has_project_id = column_exists(cursor, table_name, "project_id")

    # =====================================================
    # BULK UPLOAD (FORM — CRITICAL FIX)
    # =====================================================
    st.subheader("Bulk Upload via Excel")

    with st.form(key=f"upload_form_{st.session_state.project_id}_{selected_department}"):

        uploaded_file = st.file_uploader(
            "Upload Equipment Excel File",
            type=["xlsx"]
        )

        submit_upload = st.form_submit_button("Upload to Database")

        if submit_upload and uploaded_file:

            df_excel = pd.read_excel(uploaded_file)
            df_excel.columns = df_excel.columns.str.strip()

            rows_inserted = 0
            rows_skipped = 0

            for _, row in df_excel.iterrows():

                sr_no = safe_float(row.get("Sr. No"))
                tag_no = safe_str(row.get("Tag No."))

                if has_project_id:
                    cursor.execute(
                        f"""
                        SELECT COUNT(*) FROM {table_name}
                        WHERE project_id=? AND sr_no=? AND tag_no=?
                        """,
                        st.session_state.project_id, sr_no, tag_no
                    )
                else:
                    cursor.execute(
                        f"""
                        SELECT COUNT(*) FROM {table_name}
                        WHERE sr_no=? AND tag_no=?
                        """,
                        sr_no, tag_no
                    )

                if cursor.fetchone()[0] > 0:
                    rows_skipped += 1
                    continue

                if has_project_id:
                    cursor.execute(
                        f"""
                        INSERT INTO {table_name} (project_id, sr_no, description, uom, qty, tag_no)
                        VALUES (?,?,?,?,?,?)
                        """,
                        st.session_state.project_id,
                        sr_no,
                        safe_str(row.get("Description")),
                        safe_str(row.get("UoM")),
                        safe_float(row.get("Qty")),
                        tag_no
                    )
                else:
                    cursor.execute(
                        f"""
                        INSERT INTO {table_name} (sr_no, description, uom, qty, tag_no)
                        VALUES (?,?,?,?,?)
                        """,
                        sr_no,
                        safe_str(row.get("Description")),
                        safe_str(row.get("UoM")),
                        safe_float(row.get("Qty")),
                        tag_no
                    )

                rows_inserted += 1

            conn.commit()

            st.success(f"{rows_inserted} rows inserted")
            st.warning(f"{rows_skipped} duplicates skipped")

    # =====================================================
    # LOAD DATA
    # =====================================================
    if has_project_id:
        df = pd.read_sql(
            f"SELECT * FROM {table_name} WHERE project_id=? ORDER BY sr_no",
            conn,
            params=[st.session_state.project_id]
        )
    else:
        df = pd.read_sql(
            f"SELECT * FROM {table_name} ORDER BY sr_no",
            conn
        )

    st.subheader("Manual Equipment Entry")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_{st.session_state.project_id}_{selected_department}"
    )

    if st.button("Save Equipment Data"):
        if has_project_id:
            cursor.execute(
                f"DELETE FROM {table_name} WHERE project_id=?",
                st.session_state.project_id
            )
        else:
            cursor.execute(f"DELETE FROM {table_name}")

        for _, row in edited_df.iterrows():
            cursor.execute(
                f"""
                INSERT INTO {table_name} (sr_no, description, uom, qty, tag_no)
                VALUES (?,?,?,?,?)
                """,
                safe_float(row["sr_no"]),
                safe_str(row["description"]),
                safe_str(row["uom"]),
                safe_float(row["qty"]),
                safe_str(row["tag_no"])
            )

        conn.commit()
        st.success("✅ Equipment data saved")
