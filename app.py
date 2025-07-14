import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import traceback
import fitz  # PyMuPDF

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "✨ Exam Prep Backend is Running!"

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        uploaded_file = request.files['file']
        uploaded_file.save('uploaded.pdf')

        # ✅ Extract text from PDF
        text = ""
        with fitz.open('uploaded.pdf') as doc:
            for page in doc:
                text += page.get_text()

        return jsonify({'message': 'PDF uploaded successfully!', 'text': text})
    except Exception as e:
        print("❌ Error during PDF upload:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_questions():
    try:
        data = request.get_json()
        prompt = data.get('text', '')
        level = data.get('level', 'understand')
        print(f"📩 Prompt Received: {prompt[:100]}... | Level: {level}")

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("❌ GEMINI_API_KEY is not set in environment variables.")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Add Bloom's Taxonomy to prompt
        full_prompt = f"""
        Based on the following content, generate 5 multiple-choice questions of '{level}' difficulty level
        according to Bloom's Taxonomy. Include 4 options per question and highlight the correct answer.

        Content:
        {prompt}
        """

        response = model.generate_content(full_prompt)
        generated_text = response.text

        print("✅ Generation Successful")
        return jsonify({'questions': generated_text, 'status': 'success'})

    except Exception as e:
        print("❌ Exception in /generate endpoint")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🔧 Server running on port {port}")
    app.run(host='0.0.0.0', port=port)
