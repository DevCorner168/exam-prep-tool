import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import traceback

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
        return jsonify({'message': 'PDF uploaded successfully!'})
    except Exception as e:
        print("❌ Error during PDF upload:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_questions():
    try:
        data = request.get_json()
        prompt = data.get('text', '')
        print(f"📩 Prompt Received: {prompt}")

        # ✅ Use GEMINI_API_KEY instead of GOOGLE_API_KEY
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("❌ GEMINI_API_KEY is not set in environment variables.")

        # Configure Gemini
        print("🔑 Configuring Gemini with API Key...")
        genai.configure(api_key=api_key)

        # Load Gemini model
        model = genai.GenerativeModel('gemini-pro')

        # Generate content
        print("🚀 Generating content using Gemini...")
        response = model.generate_content(prompt)
        generated_text = response.text

        print("✅ Generation Successful")
        return jsonify({'result': generated_text})

    except Exception as e:
        print("❌ Exception in /generate endpoint")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🔧 Server running on port {port}")
    app.run(host='0.0.0.0', port=port)
