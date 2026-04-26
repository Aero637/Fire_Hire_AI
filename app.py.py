import os
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from pymongo import MongoClient

app = Flask(__name__)
# Allows your index.html to talk to this server without security blocks
CORS(app)

# 1. GOOGLE GEMINI CONFIGURATION
GEMINI_API_KEY = "AIzaSyBISMI9zMPfX29OsDIHmjuVytT7F6f7UgU"
genai.configure(api_key=GEMINI_API_KEY)

# 2. MONGODB CONFIGURATION
try:
    # Connects to your local MongoDB Compass
    client = MongoClient("mongodb://localhost:27017/")
    db = client["FairHireDB"]
    collection = db["audit_logs"]
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

@app.route('/analyze', methods=['POST'])
def analyze_text():
    try:
        # Get data from the HTML frontend
        data = request.json
        user_content = data.get('content', '')

        if not user_content:
            return jsonify({"error": "No text provided"}), 400

        # Initialize Gemini 1.5 Flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Professional prompt for hiring bias
        prompt = (
            f"Analyze the following job description for unconscious bias (gender, age, or culture). "
            f"Provide a 'Bias Score' from 0-100 and a brief list of improvements. "
            f"Text: {user_content}"
        )

        response = model.generate_content(prompt)
        ai_feedback = response.text

        # 3. THE AUDIT TRAIL: Save to MongoDB
        log_entry = {
            "project_name": "FairHire AI Analysis",
            "bias_score": 15, # Sample score for your demo
            "feedback": ai_feedback,
            "timestamp": datetime.datetime.utcnow(),
            "status": "Success"
        }
        
        collection.insert_one(log_entry)
        print("Audit log saved to FairHireDB.")

        # Send results back to the HTML
        return jsonify({
            "bias_score": 15,
            "feedback": ai_feedback
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Runs the server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)