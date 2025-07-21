import streamlit as st
import os
import re
import csv
import ollama
import json
from datetime import datetime
from course_content_gen import generate_module_content
from pages.sidebar import render_sidebar

menu = render_sidebar()
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to access this page.")
    st.stop()
username = st.session_state.username
user_courses_root = os.path.join("users", username, "courses")
st.title("Course Content Generator")
col1, col2 = st.columns(2)
if col1.button("Continue Course"):
    st.session_state.choice = "continue"
if col2.button("Revise Content"):
    st.session_state.choice = "revise"
if "choice" not in st.session_state:
    st.info("Please select an option above to continue.")
    st.stop()
if not os.path.exists(user_courses_root):
    st.error("No courses folder found. Please generate and save an outline first.")
    st.stop()
available_courses = [name for name in os.listdir(user_courses_root) if os.path.isdir(os.path.join(user_courses_root, name))]
if not available_courses:
    st.error("No courses found in your courses folder. Please generate and save an outline first.")
    st.stop()
selected_course = st.selectbox("Select a course topic:", available_courses)
course_folder = os.path.join(user_courses_root, selected_course)
outline_filename = os.path.join(course_folder, f"{selected_course}.outline")
if not os.path.exists(outline_filename):
    st.error(f"No outline file found for course '{selected_course}'.")
    st.stop()
with open(outline_filename, "r", encoding="utf-8") as f:
    outline_text = f.read()
modules_pattern = re.findall(r'(?i)^[*\s]*(?:module|unit|chapter)\s*\d*[\s:-]*\s*(.+)', outline_text, re.MULTILINE)
modules_pattern = [re.sub(r'[*\s]+$', '', m.strip()) for m in modules_pattern]
numeric_pattern = re.findall(r'^\s*\d+\.\s*([^-:\n]+)', outline_text, re.MULTILINE)
numeric_pattern = [m.strip() for m in numeric_pattern if m.strip()]
modules = modules_pattern + numeric_pattern
if not modules:
    st.info("No modules detected with regex. Using LLM for detection...")
    def detect_module_names(outline_text):
        prompt = (
            "You are an expert course outline analyzer. Given the following course outline, "
            "extract and list only the module names, one per line. Do not include any additional commentary.\n\n"
            "Course Outline:\n" + outline_text
        )
        response = ollama.chat(model="llama3:8b", messages=[{"role": "user", "content": prompt}], stream=False)
        module_names_text = response["message"]["content"]
        modules_llm = [line.strip() for line in module_names_text.splitlines() if line.strip()]
        return modules_llm
    modules = detect_module_names(outline_text)
if not modules:
    st.error("No modules available for content generation.")
    st.stop()
if st.session_state.choice == "continue":
    st.markdown("## Continue Course")
    user_scores_root = os.path.join("users", username, "scores")
    os.makedirs(user_scores_root, exist_ok=True)
    progress_csv = os.path.join(user_scores_root, "completed_modules.csv")
    completed_modules = set()
    if os.path.exists(progress_csv):
        with open(progress_csv, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Course Name"] == selected_course and row["Module Completion Status"] == "Completed":
                    completed_modules.add(row["Module Name"])
    next_module_index = len(completed_modules) + 1
    if next_module_index > len(modules):
        st.info("Congratulations! All modules have been completed for this course.")
        st.stop()
    else:
        next_module = modules[next_module_index - 1]
        st.info(f"Next module to complete: {next_module}")
        selected_module = next_module
        module_index = next_module_index
        st.session_state.selected_course = selected_course
        st.session_state.selected_module = selected_module
        st.session_state.course_folder = course_folder
    st.markdown(f"**Module:** {selected_module}")
    user_data_file = os.path.join("users", "data", f"{username}.json")
    if os.path.exists(user_data_file):
        with open(user_data_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        difficulty = user_data.get("course_difficulty", "Intermediate")
    else:
        difficulty = "Intermediate"
    expected_module_file = os.path.join(course_folder, f"module_{module_index}_content.txt")
    if os.path.exists(expected_module_file):
        if st.button("Display Existing Module Content"):
            with open(expected_module_file, "r", encoding="utf-8") as f:
                file_content = f.read()
            st.markdown(file_content)
    if st.button("Generate Content for Next Module"):
        st.session_state.module_content = ""
        st.session_state.module_completed = False
        content_placeholder = st.empty()
        try:
            for partial_content in generate_module_content(selected_module, selected_course, difficulty):
                st.session_state.module_content = partial_content
                content_placeholder.markdown(st.session_state.module_content)
            module_filename = os.path.join(course_folder, f"module_{module_index}_content.txt")
            with open(module_filename, "w", encoding="utf-8") as f:
                f.write(st.session_state.module_content)
            st.success(f"Module content saved to: {module_filename}")
            st.session_state.module_filename = module_filename
            st.session_state.module_index = module_index
        except Exception as e:
            st.error(f"Error generating content: {str(e)}")
    if "module_filename" not in st.session_state:
        if os.path.exists(expected_module_file):
            st.session_state.module_filename = expected_module_file
    if st.button("Mark Module as Completed"):
        content_exists = False
        if st.session_state.get("module_content") and st.session_state.module_content.strip():
            content_exists = True
        elif "module_filename" in st.session_state and os.path.exists(st.session_state.module_filename):
            with open(st.session_state.module_filename, "r", encoding="utf-8") as f:
                file_content = f.read()
            if file_content.strip():
                content_exists = True
        if content_exists:
            st.session_state.module_completed = True
            st.success(f"Module '{selected_module}' marked as completed!")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_record = {
                "Timestamp": timestamp,
                "Course Name": selected_course,
                "Module Name": selected_module,
                "Module Completion Status": "Completed",
                "Test Status": "Pending",
                "Score": "",
                "Total Questions": ""
            }
            records = []
            if os.path.exists(progress_csv):
                with open(progress_csv, "r", newline="", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for r in reader:
                        records.append(r)
            updated = False
            for r in records:
                if r["Course Name"] == selected_course and r["Module Name"] == selected_module:
                    r.update(new_record)
                    updated = True
                    break
            if not updated:
                records.append(new_record)
            with open(progress_csv, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Timestamp", "Course Name", "Module Name", "Module Completion Status", "Test Status", "Score", "Total Questions"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for r in records:
                    writer.writerow(r)
            st.success("Module completion status updated in CSV!")
        else:
            st.error("No module content available. Please generate content first.")
    if st.session_state.get("module_completed", False):
        if st.button("Go to MCQ Test Page for this Module"):
            if "module_filename" in st.session_state and os.path.exists(st.session_state.module_filename):
                st.query_params["page"] = "mcq"
            else:
                st.error("Module content file not found. Please generate content first.")
elif st.session_state.choice == "revise":
    st.markdown("## Revise Course Content")
    module_content_files = [f for f in os.listdir(course_folder) if re.match(r"module_\d+_content\.txt", f)]
    if module_content_files:
        module_content_files.sort(key=lambda x: int(re.search(r"module_(\d+)_content\.txt", x).group(1)))
        module_options = []
        for f in module_content_files:
            match = re.search(r"module_(\d+)_content\.txt", f)
            if match:
                module_num = int(match.group(1))
                module_name = modules[module_num - 1] if module_num - 1 < len(modules) else f"Module {module_num}"
                module_options.append((module_name, f))
        display_names = [option[0] for option in module_options]
        selected_module_name = st.selectbox("Select a module to review its content:", display_names)
        selected_file = None
        for name, file in module_options:
            if name == selected_module_name:
                selected_file = file
                break
        if st.button("Display Selected Module Content"):
            if selected_file:
                file_path = os.path.join(course_folder, selected_file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                st.markdown(content)
            else:
                st.error("Selected module file not found.")
    else:
        st.info("No former module content found.")