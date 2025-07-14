import streamlit as st
import requests
import os
import json

st.title("📚 AI-Powered Exam Preparation Tool")
st.markdown("Upload a PDF and get Bloom's Taxonomy-based multiple-choice questions.")

# Upload PDF
uploaded_file = st.file_uploader("Upload your study material (PDF only)", type="pdf")

level = st.selectbox("Select Question Difficulty Level", ["remember", "understand", "apply", "analyze", "evaluate", "create"])

if uploaded_file:
    with st.spinner("Uploading and extracting text..."):
        files = {'file': uploaded_file.getvalue()}
        try:
            res = requests.post("https://your-backend-url.onrender.com/upload", files={'file': uploaded_file})
            res.raise_for_status()
            extracted_text = res.json().get("text", "")
            st.success("✅ Text extracted successfully!")

            if st.button("Generate Questions"):
                with st.spinner("Generating questions..."):
                    gen_res = requests.post("https://your-backend-url.onrender.com/generate", json={
                        "text": extracted_text,
                        "level": level
                    })
                    gen_res.raise_for_status()
                    questions = gen_res.json().get("questions", "")
                    st.markdown("### 🎯 Generated Questions")
                    st.text_area("Review Questions Below", questions, height=300)
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to generate questions. ❌\nError: {str(e)}")
