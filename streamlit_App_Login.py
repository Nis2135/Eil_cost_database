import streamlit as st
import pyodbc

def login():

    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost\\MSSQLSERVER01;"
        "DATABASE=Cost_Estimation;"
        "Trusted_Connection=yes;"
    )

    cursor = conn.cursor()

    st.title("Cost Estimation Portal Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        query = "SELECT password_hash, role FROM app_users WHERE username=?"
        cursor.execute(query, username)

        result = cursor.fetchone()

        if result and password == result[0]:

            st.session_state.logged_in = True
            st.session_state.role = result[1]

            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid username or password")
