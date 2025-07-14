from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load your Gemini API key from environment variable
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Function to generate questions using Gemini
def generate_questions(text, level):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
    Generate 5 multiple choice questions based on the following text. 
    Follow Bloom's Taxonomy level: {level}. 
    Provide four options per question and indicate the correct answer.

    Text:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

@app.route("/")
def home():
    return "✅ Welcome to the Exam Prep Tool API"

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    
    return jsonify({"text": text})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    text = data.get("text")
    level = data.get("level")

    if not text or not level:
        return jsonify({"error": "Missing text or level"}), 400

    try:
        questions = generate_questions(text, level)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
