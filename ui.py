import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="AI Exam Prep Tool", layout="wide")
st.title("📘 AI-Powered Exam Preparation Tool")

# Upload PDF
uploaded_file = st.file_uploader("📄 Upload a PDF to extract text", type=["pdf"])
level = st.selectbox("📚 Select Bloom's Level", ["remember", "understand", "apply", "analyze", "evaluate", "create"])

text = ""
if uploaded_file:
    with st.spinner("📤 Uploading and extracting text..."):
        files = {"pdf": uploaded_file}
        res = requests.post("http://localhost:5000/upload", files=files)
        if res.status_code == 200:
            text = res.json().get("text", "")
            st.success("✅ Text extracted successfully!")
        else:
            st.error("🚨 Failed to extract text from PDF.")

if text:
    st.subheader("📝 Extracted Text")
    st.text_area("Text from PDF:", text, height=200)

    if st.button("🎯 Generate Questions"):
        with st.spinner("🧠 Generating questions..."):
            res = requests.post("http://localhost:5000/generate", json={"text": text, "level": level})
            if res.status_code == 200:
                raw_output = res.json().get("questions", "")
                st.session_state["questions_raw"] = raw_output
                st.session_state["submitted"] = False
            else:
                st.error("🚨 Failed to generate questions. Please check the backend.")

if "questions_raw" in st.session_state:
    st.subheader("📋 Practice Quiz")

    # Parse questions
    questions = []
    q_blocks = st.session_state["questions_raw"].strip().split("\n\n")
    for q_block in q_blocks:
        lines = q_block.strip().split("\n")
        if len(lines) < 6:
            continue
        question = lines[0][3:].strip()
        options = {
            "A": lines[1][3:].strip(),
            "B": lines[2][3:].strip(),
            "C": lines[3][3:].strip(),
            "D": lines[4][3:].strip(),
        }
        answer = lines[5].split(":")[1].strip()
        questions.append({
            "question": question,
            "options": options,
            "answer": answer
        })

    score = 0
    if "user_answers" not in st.session_state or not st.session_state["submitted"]:
        st.session_state["user_answers"] = {}

    with st.form("quiz_form"):
        for i, q in enumerate(questions):
            st.write(f"**Q{i+1}. {q['question']}**")
            selected = st.radio(f"Choose an answer for Q{i+1}:", list(q["options"].keys()), key=f"q{i}")
            st.session_state["user_answers"][i] = selected

        submitted = st.form_submit_button("✅ Submit Answers")
        if submitted:
            st.session_state["submitted"] = True

    # Show results
    if st.session_state["submitted"]:
        st.subheader("📊 Results")
        for i, q in enumerate(questions):
            user_ans = st.session_state["user_answers"].get(i, "")
            correct = q["answer"]
            if user_ans == correct:
                st.markdown(f"✅ **Q{i+1}: Correct**")
                score += 1
            else:
                st.markdown(f"❌ **Q{i+1}: Incorrect** (Your answer: {user_ans}, Correct: {correct})")

        st.markdown(f"### 🏁 Your Score: **{score} / {len(questions)}**")
