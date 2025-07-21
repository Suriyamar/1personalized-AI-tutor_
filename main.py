import streamlit as st
import os
import sys
from course_gen import generate_outline_stream
from pages.sidebar import render_sidebar

# Set page config first - this will be the only call in the entire app
st.set_page_config(layout="wide", page_title="Unnati - Learning Platform")

from pages.login_ui import display_login_ui

def main_app():
    menu = render_sidebar()
    st.title("📘 Course Outline Generator (Gemma 2B via Ollama)")
    course_topic = st.text_input("Enter the course topic:", "Data Structures & Algorithms")
    generate_button = st.button("🎯 Generate Outline")
    if "outline_text" not in st.session_state:
        st.session_state.outline_text = ""
    if "outline_ready" not in st.session_state:
        st.session_state.outline_ready = False
    if generate_button:
        st.session_state.outline_text = ""
        st.session_state.outline_ready = False
        outline_container = st.empty()
        prompt = (
            f"Create a clear, structured course outline on the topic '{course_topic}'. "
            "Include the course name, followed by 4 to 6 modules. For each module, provide a "
            "short description. Do not include lessons, exercises, or quizzes — only the "
            "outline and module summaries."
        )
        for partial in generate_outline_stream(prompt):
            st.session_state.outline_text = partial
            outline_container.markdown(f"**Generated Course Outline:**\n\n{st.session_state.outline_text}")
        st.session_state.outline_ready = True
    if st.session_state.outline_ready:
        if st.button("✅ OK (Save Outline)"):
            username = st.session_state.username
            user_courses_root = os.path.join("users", username, "courses")
            os.makedirs(user_courses_root, exist_ok=True)
            safe_name = "".join(c for c in course_topic if c not in r'<>:"/\|?*').strip()
            course_folder = os.path.join(user_courses_root, safe_name)
            os.makedirs(course_folder, exist_ok=True)
            filename = os.path.join(course_folder, f"{safe_name}.outline")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(st.session_state.outline_text)
            st.success(f"Course outline saved as `{filename}`.")

def main():
    # Check login status and show appropriate UI
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    if not st.session_state.logged_in:
        display_login_ui()
    else:
        main_app()

if __name__ == "__main__":
    main()