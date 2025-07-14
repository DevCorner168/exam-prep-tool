from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import os
import google.generativeai as genai

# Load your Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "Empty filename", 400

    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate", methods=["POST"])
def generate_questions():
    data = request.get_json()
    text = data.get("text", "")
    level = data.get("level", "understand")

    prompt = f"""
    Generate 5 {level}-level multiple choice questions based on Bloom's Taxonomy from the following text:

    {text}

    Format:
    1. Question?
       A. Option A
       B. Option B
       C. Option C
       D. Option D
       Answer: C
    """

    try:
        model = genai.GenerativeModel("models/gemini-pro")
        response = model.generate_content(prompt)
        return jsonify({"questions": response.text})
    except Exception as e:
        return jsonify({"error": f"Gemini API Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
