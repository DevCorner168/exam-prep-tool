from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("models/gemini-pro")
else:
    model = None

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "No file provided"}), 400

    reader = PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return jsonify({"text": text})

@app.route("/generate", methods=["POST"])
def generate_questions():
    if model is None:
        return jsonify({"error": "Gemini model not initialized"}), 500

    data = request.get_json()
    text = data.get("text", "")
    level = data.get("level", "understand")

    prompt = f"Generate 5 {level}-level questions from this text:\n{text}"
    try:
        response = model.generate_content(prompt)
        return jsonify({"questions": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
