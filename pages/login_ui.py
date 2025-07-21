import streamlit as st
from auth.login import verify_user
from auth.register import register_user
from auth.profiles import get_user_profile
import os

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def display_login_ui():
    # Create a top-level 3‑column layout so everything is centered.
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # Create tabs for Login and Registration
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        # Login Tab
        with tab1:
            st.header("Login")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                # Center the Login button
                login_cols = st.columns([2, 1, 2])
                with login_cols[1]:
                    submit_button = st.form_submit_button("Login", use_container_width=True)
                    
            if submit_button:
                if username and password:
                    user = verify_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_profile = user
                        full_name = user.get("full_name", username)
                        st.success(f"Login successful! Hello {full_name}, it's great to see you again.")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
        # Registration Tab
        with tab2:
            st.header("Register")
            
            with st.form("register_form"):
                full_name = st.text_input("Full Name")
                reg_username = st.text_input("Username")
                reg_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                age = st.text_input("Age")
                school_level = st.selectbox(
                    "School Level", ["Elementary School", "Middle School", "High School", "College"]
                )

                # Make "Create Account" wide, centered
                create_cols = st.columns([2, 1, 2])
                with create_cols[1]:
                    submit_register = st.form_submit_button("Create Account", use_container_width=True)
                    
            if submit_register:
                if full_name and reg_username and reg_password and confirm_password and age:
                    if reg_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = register_user(full_name, reg_username, reg_password, age, school_level)
                        if success:
                            st.success(message)
                            # Switch to login tab
                            st.session_state.active_tab = 0
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")