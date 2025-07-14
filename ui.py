import streamlit as st
import requests
import os
import json

# Backend URL
BACKEND_URL = "https://exam-prep-tool.onrender.com"

st.set_page_config(page_title="AI Exam Prep Tool", page_icon="📘")
st.title("📚 AI-Powered Exam Preparation Tool")
st.markdown("Upload a PDF and get Bloom's Taxonomy-based multiple-choice questions.")

# Upload PDF
uploaded_file = st.file_uploader("Upload your study material (PDF only)", type="pdf")

# Bloom's Taxonomy Levels
level = st.selectbox(
    "Select Question Difficulty Level",
    ["remember", "understand", "apply", "analyze", "evaluate", "create"]
)

# When a file is uploaded
if uploaded_file:
    with st.spinner("📄 Uploading and extracting text from PDF..."):
        try:
            # Send PDF to backend /upload
            upload_response = requests.post(
                f"{BACKEND_URL}/upload", 
                files={'file': uploaded_file}
            )
            upload_response.raise_for_status()

            # Extract text from response
            extracted_text = upload_response.json().get("text", "")
            st.success("✅ Text extracted successfully!")

            # Button to generate questions
            if st.button("Generate Questions"):
                with st.spinner("🧠 Generating questions..."):
                    generate_response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json={"text": extracted_text, "level": level}
                    )
                    generate_response.raise_for_status()

                    questions = generate_response.json().get("questions", "")
                    st.markdown("### 🎯 Generated Questions")
                    st.text_area("Review Questions Below", questions, height=300)

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to generate questions.\n\n**Error:** {str(e)}")
