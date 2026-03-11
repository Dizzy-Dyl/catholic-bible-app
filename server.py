import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json()
    question = (data or {}).get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    if not GROQ_API_KEY:
        return jsonify({"answer": "Set GROQ_API_KEY for free AI!"})

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant", 
                "messages": [
                    {
                        "role": "system",
                        "content": "Catholic AI assistant. Brief, Catechism-based answers about Scripture."
                    },
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        answer = data["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "AI request failed"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
