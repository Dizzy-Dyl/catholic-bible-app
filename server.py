from email.policy import default
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

@app.route("/bible/<int:book_id>/<int:chapter_id>", methods=["GET"])
def bible(book_id, chapter_id):
    try:
        translation = request.args.get("translation", "WEB")
        if translation == "RVR1960":
            book_names: list = ["genesis","exodus","leviticus","numbers","deuteronomy","joshua","judges","ruth","1-samuel","2-samuel","1-kings","2-kings","1-chronicles","2-chronicles","ezra","nehemiah","esther","job","psalms","proverbs","ecclesiastes","song-of-songs","isaiah","jeremiah","lamentations","ezekiel","daniel","hosea","joel","amos","obadiah","jonah","micah","nahum","habakkuk","zephaniah","haggai","zechariah","malachi","matthew","mark","luke","john)","acts)","romans)","1-corinthians)","2-corinthians)","galatians)","ephesians)","philippians)","colossians)","1-thessalonians)","2-thessalonians)","1-timothy)","2-timothy)","titus)","philemon)","hebrews)","james)","1-peter)","2-peter)","1-john)","2-john)","3-john)","jude)","revelation)"]
            book = book_names[book_id - 1]
            url = f"https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles/es-rvr1909/books/{book}/chapters/{chapter_id}.json"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            raw = resp.json()
            verses = [{"verseId": v.get("verse"), "verse": v.get("text", "")} for v in raw]
            return jsonify(verses)
        else:
            url = f"https://bible-go-api.rkeplin.com/v1/books/{book_id}/chapters/{chapter_id}"
            resp = requests.get(url, params={"translation": translation}, timeout=15)
            resp.raise_for_status()
            return jsonify(resp.json())
    except Exception as e:
        print("BIBLE ERROR:", e)
        return jsonify({"error": "Could not fetch chapter"}), 500