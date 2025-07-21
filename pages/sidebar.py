import streamlit as st

def render_sidebar():
    if not st.session_state.get("logged_in", False):
        return None
    menu = st.sidebar.radio("Navigation", ["Main", "Preassessment", "Course Selection", "Content UI", "MCQ"])
    if menu == "Main":
        st.query_params["page"] = "main"
    elif menu == "Preassessment":
        st.query_params["page"] = "preassessment"
    elif menu == "Course Selection":
        st.query_params["page"] = "course_selection"
    elif menu == "Content UI":
        st.query_params["page"] = "content_ui"
    elif menu == "MCQ":
        st.query_params["page"] = "mcq"