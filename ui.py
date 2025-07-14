import streamlit as st
import requests
import json
from datetime import datetime
import os

st.set_page_config(page_title="🧠 AI Exam Prep Tool", layout="centered")

st.title("📚 AI-Powered Exam Preparation Tool")
st.write("Upload a PDF and get multiple-choice questions instantly based on Bloom's Taxonomy!")

# Save progress function
def save_progress(level, num_questions):
    progress_file = "progress.json"
    progress = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "num_questions": num_questions
    }

    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(progress)

    with open(progress_file, "w") as f:
        json.dump(data, f, indent=4)

# Upload file
uploaded_file = st.file_uploader("📄 Upload your PDF", type=["pdf"])

# Choose difficulty level
level = st.selectbox(
    "🎯 Select Bloom's Taxonomy Level",
    ["remember", "understand", "apply", "analyze", "evaluate", "create"]
)

# Store session data
if "questions" not in st.session_state:
    st.session_state["questions"] = ""

if uploaded_file is not None:
    if st.button("⚙️ Generate Questions"):
        files = {"file": uploaded_file.getvalue()}
        data = {"level": level}
        try:
            res = requests.post("http://localhost:5000/upload", files=files, data=data)
            if res.status_code == 200:
                response = requests.post("http://localhost:5000/generate", json=res.json())
                if response.status_code == 200:
                    questions = response.json()["questions"]
                    st.session_state["questions"] = questions
                    st.success("✅ Questions generated successfully!")
                    st.text_area("📋 Your Questions", value=questions, height=400)

                    # Save to progress
                    save_progress(level, len(questions.split("Question")) - 1)

                    # Allow download
                    st.download_button(
                        label="📥 Download as .txt",
                        data=questions,
                        file_name="mcqs.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("❌ Failed to generate questions. Please check the backend.")
            else:
                st.error("❌ Failed to upload PDF. Check backend.")
        except Exception as e:
            st.error(f"🚨 Error: {e}")

# Show progress
if st.button("📊 View My Progress"):
    if os.path.exists("progress.json"):
        with open("progress.json", "r") as f:
            data = json.load(f)

        if data:
            st.subheader("🧠 Quiz History")
            for i, entry in enumerate(data[::-1], 1):
                st.markdown(f"""
**#{i}**  
🕒 Time: `{entry['timestamp']}`  
🎯 Level: `{entry['level']}`  
❓ Questions: `{entry['num_questions']}`  
---
                """)
        else:
            st.info("No progress yet. Start generating some questions!")
    else:
        st.warning("Progress tracking file not found.")
