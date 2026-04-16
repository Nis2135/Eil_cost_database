
import streamlit as st
import pyodbc
import pandas as pd

import Department
import Template_Manager


# ==================================================
# DATABASE CONNECTION
# ==================================================
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\MSSQLSERVER01;"
        "DATABASE=Cost_Estimation;"
        "Trusted_Connection=yes;"
    )


# ==================================================
# PROJECT MANAGER PAGE
# ==================================================
def project_manager():

    st.title("Project Manager")

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------
    # CREATE PROJECT
    # ----------------------------
    st.subheader("Create New Project")

    project_name = st.text_input("Project Name")
    description = st.text_area("Description")

    if st.button("Create Project"):

        project_name = project_name.strip().title()

        if not project_name:
            st.error("Project name is required")

        else:

            # CHECK DUPLICATE PROJECT
            exists = cursor.execute(
                "SELECT COUNT(*) FROM projects WHERE project_name = ?",
                project_name
            ).fetchone()[0]

            if exists > 0:
                st.warning("Project already exists. Please choose a different name.")

            else:

                cursor.execute(
                    "INSERT INTO projects (project_name, description) VALUES (?, ?)",
                    project_name,
                    description
                )

                conn.commit()

                pid = cursor.execute(
                    "SELECT TOP 1 project_id FROM projects WHERE project_name=? ORDER BY created_at DESC",
                    project_name
                ).fetchone()[0]

                st.session_state.project_id = int(pid)
                st.session_state.project_name = project_name
                st.session_state.current_page = "Dashboard"

                st.success("Project created successfully")

                st.rerun()

    st.divider()

    # ----------------------------
    # EXISTING PROJECTS
    # ----------------------------
    st.subheader("Existing Projects")

    df = pd.read_sql(
        "SELECT project_id, project_name FROM projects ORDER BY project_name",
        conn
    )

    for _, row in df.iterrows():

        col1, col2 = st.columns([6, 1])

        with col1:
            st.write(row["project_name"])

        with col2:
            if st.button("Delete", key="del_" + str(row["project_id"])):

                st.session_state.delete_project_id = int(row["project_id"])
                st.session_state.delete_project_name = row["project_name"]

    # ----------------------------
    # DELETE CONFIRMATION
    # ----------------------------
    if "delete_project_id" in st.session_state:

        st.warning(
            "Are you sure you want to delete project "
            + st.session_state.delete_project_name +
            "? This will permanently remove all related data."
        )

        col_yes, col_no = st.columns(2)

        with col_yes:

            if st.button("Yes, Delete Project"):

                cursor.execute(
                    "DELETE FROM projects WHERE project_id = ?",
                    st.session_state.delete_project_id
                )

                conn.commit()

                if st.session_state.project_id == st.session_state.delete_project_id:

                    st.session_state.project_id = None
                    st.session_state.project_name = None
                    st.session_state.current_page = "Project Manager"

                del st.session_state.delete_project_id
                del st.session_state.delete_project_name

                st.success("Project deleted successfully")

                st.rerun()

        with col_no:

            if st.button("Cancel"):

                del st.session_state.delete_project_id
                del st.session_state.delete_project_name

                st.rerun()


# ==================================================
# MAIN ROUTER
# ==================================================
def main():

    # ======================================
    # SESSION STATE INITIALIZATION
    # ======================================
    defaults = {
        "project_id": None,
        "project_name": None,
        "current_page": "Dashboard",
        "pm_expanded": True,
        "last_project_id": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    conn = get_connection()

    projects = pd.read_sql(
        "SELECT project_id, project_name FROM projects ORDER BY project_name",
        conn
    )

    # ======================
    # SIDEBAR
    # ======================
    with st.sidebar:

        st.title("Navigation")

        toggle_label = (
            "Project Manager"
            if st.session_state.pm_expanded
            else "Project Manager"
        )

        if st.button(toggle_label):
            st.session_state.pm_expanded = not st.session_state.pm_expanded

        if st.session_state.pm_expanded and not projects.empty:

            project_names = projects["project_name"].tolist()

            if st.session_state.project_name in project_names:
                current_index = project_names.index(st.session_state.project_name)
            else:
                current_index = 0

            selected_project = st.selectbox(
                "Select Project",
                project_names,
                index=current_index
            )

            if selected_project != st.session_state.project_name:

                row = projects[
                    projects["project_name"] == selected_project
                ].iloc[0]

                st.session_state.project_id = int(row["project_id"])
                st.session_state.project_name = selected_project
                st.session_state.current_page = "Dashboard"

        st.divider()

        nav_options = ["Dashboard", "Template Manager", "Project Manager"]

        if st.session_state.current_page not in nav_options:
            st.session_state.current_page = "Dashboard"

        nav_index = nav_options.index(st.session_state.current_page)

        page = st.radio("Go to", nav_options, index=nav_index)

    # ======================
    # MAIN CONTENT
    # ======================
    if page != st.session_state.current_page:
        st.session_state.current_page = page

    if st.session_state.current_page == "Project Manager":

        project_manager()

    elif st.session_state.current_page == "Dashboard":

        if st.session_state.project_id is None:
            st.warning("Please select or create a project")
        else:
            Department.equipment_dashboard()

    else:

        if st.session_state.project_id is None:
            st.warning("Please select or create a project")
        else:
            Template_Manager.show()

