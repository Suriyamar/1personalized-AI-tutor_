import streamlit as st
import os
import re
import csv
import random
from datetime import datetime
from mcq_gen import generate_mcq
from pages.sidebar import render_sidebar

st.title("MCQ Test for Module")
if st.button("Reset MCQ State"):
    st.session_state.loaded_questions = None
    st.session_state.user_answers = {}
    st.session_state.score = None
    username = st.session_state.username if "username" in st.session_state else "default"
    user_courses_root = os.path.join("users", username, "courses")
    temp_csv = os.path.join(user_courses_root, "temp_mcqs.csv")
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
    st.success("Session state and temp CSV cleared. Please generate fresh MCQs.")
menu = render_sidebar()
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to access this page.")
    st.stop()
if "loaded_questions" not in st.session_state:
    st.session_state.loaded_questions = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "score" not in st.session_state:
    st.session_state.score = None
username = st.session_state.username
user_courses_root = os.path.join("users", username, "courses")
if not os.path.exists(user_courses_root):
    st.error("No courses folder found.")
    st.stop()
available_courses = [name for name in os.listdir(user_courses_root) if os.path.isdir(os.path.join(user_courses_root, name))]
if not available_courses:
    st.error("No courses found in your courses folder.")
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
    st.error("No modules detected in the outline. Please ensure the outline contains module names.")
    st.stop()
selected_module = st.selectbox("Select a module for MCQ generation:", modules)
module_index = modules.index(selected_module) + 1
module_filename = os.path.join(course_folder, f"module_{module_index}_content.txt")
st.subheader(f"Course: {selected_course}")
st.subheader(f"Module: {selected_module}")
if not os.path.exists(module_filename):
    st.error(f"Module content file not found: {module_filename}. Please generate the module content first.")
    st.stop()
try:
    with open(module_filename, "r", encoding="utf-8") as f:
        file_module_content = f.read()
    if not file_module_content.strip():
        st.error("Module content file is empty.")
        st.stop()
except Exception as e:
    st.error(f"Error reading module content: {str(e)}")
    st.stop()
def retrieve_additional_context(module_content):
    additional_context = "\nAdditional Context:\n- Key definitions\n- Supplementary examples\n- Important dates and figures\n"
    return additional_context
retrieved_context = retrieve_additional_context(file_module_content)
def parse_mcq_output_primary(mcq_text):
    question_blocks = re.split(r'\*\*Question\s+\d+:\s*', mcq_text, flags=re.IGNORECASE)
    questions = []
    for block in question_blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        question_text = lines[0].strip()
        if not question_text:
            continue
        current_question = {"question": question_text, "options": [], "correct": ""}
        option_pattern = re.compile(r'([A-D])\)\s*(.*)')
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("**answer**"):
                answer_match = re.search(r'\*\*Answer:\*\*\s*([A-D])', line, re.IGNORECASE)
                if answer_match:
                    current_question["correct"] = answer_match.group(1).strip()
            else:
                opt_match = option_pattern.match(line)
                if opt_match:
                    label = opt_match.group(1)
                    text = opt_match.group(2).strip()
                    current_question["options"].append((label, text))
        if current_question["options"]:
            questions.append(current_question)
    return questions
def extract_answers_from_context(questions, mcq_text):
    for i, q in enumerate(questions):
        if not q["correct"]:
            simple_q = re.sub(r'[^\w\s]', '', q["question"].lower())
            q_area = re.search(f".*?{simple_q}.*?\\*\\*Answer:\\*\\*\\s*([A-D])", mcq_text, re.IGNORECASE | re.DOTALL)
            if q_area:
                q["correct"] = q_area.group(1)
                continue
            for opt, text in q["options"]:
                if any(hint in text.lower() for hint in ["(correct)", "*correct*", "[correct]"]):
                    q["correct"] = opt
                    break
    return questions
def parse_mcq_output(mcq_text):
    questions = parse_mcq_output_primary(mcq_text)
    questions = extract_answers_from_context(questions, mcq_text)
    answered_questions = [q for q in questions if q["correct"]]
    if answered_questions:
        answer_freq = {"A": 0, "B": 0, "C": 0, "D": 0}
        for q in answered_questions:
            if q["correct"] in answer_freq:
                answer_freq[q["correct"]] += 1
        most_common = max(answer_freq, key=answer_freq.get)
        for q in questions:
            if not q["correct"]:
                q["correct"] = most_common
    return questions
def clean_question_text(raw_text):
    cleaned = raw_text.strip().strip('"""\'\'')
    cleaned = re.sub(r'^\s*Question\s*\d+\s*[:.-]*\s*', '', cleaned, flags=re.IGNORECASE)
    return cleaned
if st.button("Generate Test (MCQs) for this Module"):
    with st.spinner("Generating MCQs..."):
        try:
            mcq_output = generate_mcq(file_module_content, retrieved_context, num_questions=15)
        except Exception as e:
            st.error(f"Failed to generate MCQs: {str(e)}")
            st.stop()
    questions = parse_mcq_output(mcq_output)
    if len(questions) == 0:
        st.error("No valid questions could be parsed from the model output. Please try regenerating.")
        st.stop()
    else:
        valid_questions = [q for q in questions if q["correct"]]
        if len(valid_questions) < len(questions):
            st.warning(f"Found {len(questions)} questions but only {len(valid_questions)} have answers. The remaining questions will use best-guess answers.")
        if len(questions) > 10:
            questions_to_use = valid_questions[:10]
            if len(questions_to_use) < 10:
                remaining = [q for q in questions if q not in valid_questions]
                questions_to_use.extend(remaining[:10 - len(questions_to_use)])
            questions = questions_to_use
        elif len(questions) < 10:
            st.warning(f"Only {len(questions)} questions were generated. Proceeding with these.")
        temp_csv = os.path.join(course_folder, "temp_mcqs.csv")
        with open(temp_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["question", "option_A", "option_B", "option_C", "option_D", "correct"])
            for q in questions:
                opts = {label: text for label, text in q["options"]}
                row = [
                    q["question"],
                    opts.get("A", ""),
                    opts.get("B", ""),
                    opts.get("C", ""),
                    opts.get("D", ""),
                    q["correct"]
                ]
                writer.writerow(row)
        loaded_questions = []
        with open(temp_csv, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                options = [("A", row["option_A"]), ("B", row["option_B"]), ("C", row["option_C"]), ("D", row["option_D"])]
                loaded_questions.append({
                    "question": row["question"],
                    "options": options,
                    "correct": row["correct"]
                })
        st.session_state.loaded_questions = loaded_questions
        st.success("MCQs generated, saved as temp CSV, and loaded into the test!")
if st.session_state.loaded_questions:
    st.markdown("### MCQ Test")
    for i, q in enumerate(st.session_state.loaded_questions, start=1):
        cleaned_text = clean_question_text(q['question'])
        st.markdown(f"**Question {i}:** {cleaned_text}")
        options_list = [f"{label}: {text}" for label, text in q["options"]]
        user_choice = st.radio(f"Select your answer for Question {i}:", options_list, key=f"q{i}")
        st.session_state.user_answers[i] = user_choice.split(":")[0]
    if st.button("Submit Answers"):
        score = 0
        total_questions = len(st.session_state.loaded_questions)
        for i, q in enumerate(st.session_state.loaded_questions, start=1):
            user_choice = st.session_state.user_answers.get(i, "")
            if user_choice == q["correct"]:
                score += 1
        percentage = (score / total_questions) * 100
        st.markdown(f"**Your Score: {score} out of {total_questions} ({percentage:.1f}%)**")
        if percentage >= 80:
            st.success("Congratulations! You passed the test. You can move on to the next module.")
            st.session_state.score = score
            user_scores_root = os.path.join("users", username, "scores")
            os.makedirs(user_scores_root, exist_ok=True)
            completed_csv = os.path.join(user_scores_root, "completed_modules.csv")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            module_completion_status = "Completed"
            test_status = "Completed"
            record = [
                timestamp,
                selected_course,
                selected_module,
                module_completion_status,
                test_status,
                score,
                total_questions
            ]
            file_exists = os.path.isfile(completed_csv)
            with open(completed_csv, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(["Timestamp", "Course Name", "Module Name", "Module Completion Status", "Test Status", "Score", "Total Questions"])
                writer.writerow(record)
        else:
            st.error("Your score is less than 80%. Please retake the test to progress.")
            if st.button("Retake Test"):
                st.session_state.loaded_questions = None
                st.session_state.user_answers = {}