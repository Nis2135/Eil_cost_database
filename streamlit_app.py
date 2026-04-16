import streamlit as st
from streamlit_App_Login import login
import Main_Page_Launcher

# session control
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# login gate
if not st.session_state.logged_in:
    login()
    st.stop()


# -----------------------------
# MAIN APPLICATION
# -----------------------------

Main_Page_Launcher.main()


# logout
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()




