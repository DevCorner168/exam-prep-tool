from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader

# Load API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Initialize model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

# Upload PDF Route
@app.route("/upload", methods=["POST"])
def upload_pdf():
    try:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        
        print("✅ PDF text extracted.")
        return jsonify({"text": text})
    
    except Exception as e:
        print("🚨 PDF Upload Error:", e)
        return jsonify({"error": str(e)}), 500

# Generate Questions Route
@app.route("/generate", methods=["POST"])
def generate_questions():
    try:
        data = request.get_json()
        text = data.get("text", "")
        level = data.get("level", "understand")

        print("📩 Received text and level:", level)

        prompt = f"""
        Based on Bloom's Taxonomy, generate 5 multiple choice questions at the '{level}' level from the following content:

        {text}

        Format:
        1. Question?
           A. Option A
           B. Option B
           C. Option C
           D. Option D
           Answer: C
        """

        response = model.generate_content(prompt)
        result = response.text.strip()

        print("✅ Gemini response generated.")
        return jsonify({"questions": result})

    except Exception as e:
        print("🚨 Gemini API Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
