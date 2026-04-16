import streamlit as st
import pandas as pd
import pyodbc


def show():

    st.title("Template Manager")

    tab1, tab2, tab3 = st.tabs([
        "Facilities Manager",
        "Cost Categories",
        "Cost Entry"
    ])

    # -------------------------
    # SQL CONNECTION
    # -------------------------

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\MSSQLSERVER01;"
        "DATABASE=Cost_Estimation;"
        "Trusted_Connection=yes;"
    )

    cursor = conn.cursor()

    # =========================
    # TAB 1 — FACILITIES MANAGER
    # =========================

    with tab1:

        st.header("Facilities Manager")

        if st.button("➕ Add Facility"):

            cursor.execute(
                """
                INSERT INTO facilities (facility_name, strategy)
                VALUES ('New Facility','Strategy')
                """
            )

            conn.commit()
            st.rerun()

        query = """
        SELECT id, facility_name, strategy
        FROM facilities
        ORDER BY id
        """

        df = pd.read_sql(query, conn)

        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            disabled=["id"]
        )

        if st.button("Save Facilities Changes"):

            cursor.execute("DELETE FROM facilities")

            for _, row in edited_df.iterrows():

                cursor.execute(
                    """
                    INSERT INTO facilities (facility_name, strategy)
                    VALUES (?, ?)
                    """,
                    row["facility_name"],
                    row["strategy"]
                )

            conn.commit()

            st.success("Facilities updated successfully")

    # =========================
    # TAB 2 — COST CATEGORIES
    # =========================

    with tab2:

        st.header("Cost Categories")

        if st.button("➕ Add Category"):

            cursor.execute(
                """
                INSERT INTO cost_categories (category_name, parent_category, order_index)
                VALUES ('New Category','EPC',1)
                """
            )

            conn.commit()
            st.rerun()

        query = """
        SELECT id, category_name, parent_category, order_index
        FROM cost_categories
        ORDER BY order_index
        """

        df = pd.read_sql(query, conn)

        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            disabled=["id"]
        )

        if st.button("Save Category Changes"):

            cursor.execute("DELETE FROM cost_categories")

            for _, row in edited_df.iterrows():

                cursor.execute(
                    """
                    INSERT INTO cost_categories (category_name, parent_category, order_index)
                    VALUES (?, ?, ?)
                    """,
                    row["category_name"],
                    row["parent_category"],
                    row["order_index"]
                )

            conn.commit()

            st.success("Categories updated successfully")

    # =========================
    # TAB 3 — COST ENTRY MATRIX
    # =========================

    with tab3:

        st.header("Cost Output")

        # -------------------------
        # LOAD FACILITIES
        # -------------------------

        facilities_query = """
        SELECT facility_name
        FROM facilities
        ORDER BY id
        """

        facilities = pd.read_sql(facilities_query, conn)

        # -------------------------
        # LOAD COST CATEGORIES
        # -------------------------

        categories_query = """
        SELECT category_name
        FROM cost_categories
        ORDER BY order_index
        """

        categories = pd.read_sql(categories_query, conn)

        # -------------------------
        # BUILD MATRIX
        # -------------------------

        matrix = pd.DataFrame()

        matrix["Category"] = categories["category_name"]

        for facility in facilities["facility_name"]:
            matrix[facility] = 0

        # -------------------------
        # DISPLAY EDITABLE MATRIX
        # -------------------------

        edited_matrix = st.data_editor(
            matrix,
            use_container_width=True
        )

        st.info("Cost matrix generated dynamically from Facilities and Cost Categories.")
