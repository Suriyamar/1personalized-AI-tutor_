import streamlit as st
import csv
import os
import random
import json
from datetime import datetime
from pages.sidebar import render_sidebar

st.title("Preassessment Test")
menu = render_sidebar()
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login to take the preassessment test.")
    st.stop()
if "user_profile" in st.session_state and "school_level" in st.session_state.user_profile:
    school_level = st.session_state.user_profile["school_level"]
    username = st.session_state.user_profile["username"]
else:
    st.error("School level information not found in user profile.")
    st.stop()
if school_level == "Elementary School":
    test_file = "Elementary_MCQ_Full_Set.csv"
elif school_level == "Middle School":
    test_file = "Middle_School_MCQ_Test_Full.csv"
elif school_level == "High School":
    test_file = "High_School_MCQ_Test_Full.csv"
else:
    st.error("Invalid school level in profile.")
    st.stop()
test_file_path = os.path.join("preassessment", test_file)
if not os.path.exists(test_file_path):
    st.error(f"Test file not found for {school_level} at path: {test_file_path}")
    st.stop()
questions = []
with open(test_file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        questions.append(row)
if len(questions) == 0:
    st.error("No questions available for the preassessment test.")
    st.stop()
num_questions = 50
if len(questions) > num_questions:
    random.seed(username)
    selected_questions = random.sample(questions, num_questions)
else:
    selected_questions = questions
    num_questions = len(questions)
if "preassessment_answers" not in st.session_state:
    st.session_state.preassessment_answers = {}
user_data_dir = os.path.join("users", "data")
os.makedirs(user_data_dir, exist_ok=True)
user_file = os.path.join(user_data_dir, f"{username}.json")
if os.path.exists(user_file):
    with open(user_file, "r") as f:
        user_data = json.load(f)
    if "preassessment" in user_data:
        st.info("You have already completed the preassessment test.")
        preassessment_data = user_data["preassessment"]
        st.write(f"**Score:** {preassessment_data['score']:.1f}%")
        st.write(f"**Difficulty Level:** {preassessment_data['difficulty']}")
        st.write(f"**Completed on:** {preassessment_data['date']}")
        if st.button("Retake Assessment"):
            user_data.pop("preassessment", None)
            with open(user_file, "w") as f:
                json.dump(user_data, f, indent=4)
            st.session_state.preassessment_answers = {}
            st.rerun()
        else:
            st.stop()
st.markdown("### Answer the following questions:")
for i, q in enumerate(selected_questions, start=1):
    question_text = q.get('Question', '')
    st.markdown(f"**Question {i}:** {question_text}")
    option_a = q.get('Option A', '').strip()
    option_b = q.get('Option B', '').strip()
    option_c = q.get('Option C', '').strip()
    option_d = q.get('Option D', '').strip()
    options = [
        f"A: {option_a}",
        f"B: {option_b}",
        f"C: {option_c}",
        f"D: {option_d}"
    ]
    selected_answer = st.radio("Select your answer:", options, key=f"pa_q{i}")
    st.session_state.preassessment_answers[i] = selected_answer.split(":")[0].strip().upper()
    st.markdown("---")
if st.button("Submit Preassessment"):
    score = 0
    incorrect_answers = []
    detailed_results = []
    for i, q in enumerate(selected_questions, start=1):
        user_choice = st.session_state.preassessment_answers.get(i, "")
        correct_answer = ""
        if "Answer Key" in q:
            correct_answer = q.get("Answer Key", "").strip().upper()
        elif "Correct Answer" in q:
            correct_answer = q.get("Correct Answer", "").strip().upper()
            if len(correct_answer) > 1 and correct_answer[1] == ")":
                correct_answer = correct_answer[0]
        is_correct = user_choice == correct_answer
        if is_correct:
            score += 1
        else:
            incorrect_answers.append({
                "Question": i,
                "Your Answer": user_choice,
                "Correct Answer": correct_answer
            })
        detailed_results.append({
            "question_number": i,
            "question_text": q.get('Question', ''),
            "user_answer": user_choice,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
    percentage = (score / num_questions) * 100
    st.session_state.preassessment_score = percentage
    if percentage < 40:
        difficulty = "Beginner"
    elif percentage < 70:
        difficulty = "Intermediate"
    else:
        difficulty = "Advanced"
    st.session_state.course_difficulty = difficulty
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {
            "username": username,
            "school_level": school_level,
        }
    user_data["preassessment"] = {
        "score": percentage,
        "correct_answers": score,
        "total_questions": num_questions,
        "difficulty": difficulty,
        "date": current_date,
        "detailed_results": detailed_results
    }
    user_data["course_difficulty"] = difficulty
    with open(user_file, "w") as f:
        json.dump(user_data, f, indent=4)
    if "user_profile" in st.session_state:
        st.session_state.user_profile["course_difficulty"] = difficulty
    st.success(f"Test completed! Your score: {score} out of {num_questions} ({percentage:.1f}%)")
    st.info(f"Recommended Course Difficulty: {difficulty}")
    st.success("Your results have been saved to your user profile.")
    if incorrect_answers:
        with st.expander("Review incorrect answers"):
            for item in incorrect_answers:
                q_num = item['Question']
                q_text = selected_questions[q_num-1].get('Question', '')
                st.markdown(f"**Question {q_num}:** {q_text}")
                st.markdown(f"- Your answer: **{item['Your Answer']}**")
                st.markdown(f"- Correct answer: **{item['Correct Answer']}**")
                st.markdown("---")