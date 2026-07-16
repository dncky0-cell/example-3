import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {
    "origins": [
        "https://chatbuddy.school", 
        "https://www.chatbuddy.school", 
        "https://aischools.netlify.app"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

SOCRATIC_PROMPT = """
you are chat buddy an intelligent socratic tutor for students

if they ask a math or homework question explain the concept first instead of just giving the answer or asking what do you think and never give the final answer just guide them step by step but if they are just chatting normally with no homework involved you can be friendly and chat directly keep the tone short encouraging and use emojis occasionally
"""

API_KEY = "." # not mentioned ofc
API_URL = "." # same with this one
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

@app.route('/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "No data received"}), 400

        user_message = data.get("message", "")
        history = data.get("history", []) 
        
        messages_payload = [
            {"role": "system", "content": SOCRATIC_PROMPT}
        ]

        if history and isinstance(history, list):
            messages_payload.extend(history)

        messages_payload.append({"role": "user", "content": user_message})

        payload = {
            "model": MODEL_NAME,
            "messages": messages_payload,
            "temperature": 0.5
        }

        headers = {
            "Authorization": f"Bearer {API_KEY.strip()}",
            "Content-Type": "application/json"
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return jsonify({"error": "AI API Error", "details": response.text}), response.status_code

        ai_response_content = response.json()['choices'][0]['message']['content']
        
        return jsonify({
            "message": {
                "content": ai_response_content,
                "role": "assistant"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
