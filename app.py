from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()
from flask_socketio import SocketIO, emit
import os, json, time, requests as http_requests
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'student-chat-secret-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Use gevent on Render (production), threading locally (Python 3.14 compat)
import os as _os
_async_mode = "gevent" if _os.environ.get("RENDER") else "threading"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=_async_mode,
                    max_http_buffer_size=16 * 1024 * 1024)

# ── Groq Setup — Pure HTTP (Python 3.14 compatible) ───
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
MODEL        = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are StudyBot - a friendly AI study assistant for students.
- Explain concepts clearly with step-by-step breakdowns
- Use examples and analogies to make topics easy
- Support Tamil and English (code-switch if student writes in Tamil)
- Be warm, encouraging, and motivating
- Format answers with numbered steps when needed
- Start every response with a relevant emoji"""

# ── Data Stores ───────────────────────────────────────
active_users = {}
chat_history = []
user_stats   = {}

def get_stats(username):
    if username not in user_stats:
        user_stats[username] = {
            "questions": 0, "quiz_scores": [],
            "study_sessions": 0, "notes": [],
            "joined_at": datetime.now().strftime("%d %b %Y"),
        }
    return user_stats[username]

# ── Groq HTTP helper (no external library needed) ─────
def groq_call(messages, max_retries=4):
    """Call Groq REST API using requests library."""
    delay = 10
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1500,
        "temperature": 0.7
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }

    for attempt in range(max_retries):
        try:
            resp = http_requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
            if resp.status_code == 429:
                if attempt < max_retries - 1:
                    print(f"Rate limited. Waiting {delay}s... (retry {attempt+2}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise RuntimeError("Rate limit reached. Wait 1 minute and try again!")
            if resp.status_code != 200:
                raise RuntimeError(f"Groq API error {resp.status_code}: {resp.text}")
            return resp.json()["choices"][0]["message"]["content"]
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}")

def groq_ask(prompt, system=SYSTEM_PROMPT):
    return groq_call([
        {"role": "system", "content": system},
        {"role": "user",   "content": prompt}
    ])

def groq_json(prompt):
    return groq_call([
        {"role": "system", "content": "Respond with ONLY valid JSON. No markdown, no extra text."},
        {"role": "user",   "content": prompt}
    ])

def clean_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    return raw

# ── Routes ────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    try:
        data     = request.json
        pdf_text = data.get("text", "").strip()
        filename = data.get("filename", "document.pdf")
        username = data.get("username", "Student")
        if not pdf_text:
            return jsonify({"error": "No text found in PDF"}), 400
        if len(pdf_text) > 12000:
            pdf_text = pdf_text[:12000] + "\n\n[... truncated ...]"
        prompt = (
            f'PDF: "{filename}"\n\nContent:\n{pdf_text}\n\n'
            "1) Brief summary (3-4 sentences)\n"
            "2) Top 5 key points\n"
            "3) 3 exam-style questions"
        )
        summary = groq_ask(prompt)
        get_stats(username)["notes"].append({
            "title":    f"PDF: {filename}",
            "content":  summary,
            "saved_at": datetime.now().strftime("%d %b %Y, %H:%M"),
            "source":   "pdf"
        })
        bot_msg = {
            "type": "bot", "username": "StudyBot",
            "message": f"PDF Uploaded: {filename}\n\n{summary}",
            "timestamp": datetime.now().strftime("%H:%M"), "sid": "bot",
        }
        chat_history.append(bot_msg)
        socketio.emit("new_message", bot_msg)
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    try:
        data    = request.json
        topic   = data.get("topic", "").strip()
        subject = data.get("subject", "General")
        count   = min(int(data.get("count", 5)), 10)
        if not topic:
            return jsonify({"error": "Topic required"}), 400
        prompt = (
            f'Generate {count} MCQ questions about "{topic}" for {subject} students. '
            "Medium difficulty. Use exactly this JSON format:\n"
            '{"questions":[{"q":"...","options":["A) ...","B) ...","C) ...","D) ..."],"answer":"A","explanation":"..."}]}'
        )
        raw       = clean_json(groq_json(prompt))
        quiz_data = json.loads(raw)
        return jsonify({"success": True, "quiz": quiz_data, "topic": topic, "subject": subject})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-note", methods=["POST"])
def save_note():
    try:
        data  = request.json
        stats = get_stats(data.get("username", "Student"))
        stats["notes"].append({
            "title":    data.get("title", "Note"),
            "content":  data.get("content", ""),
            "saved_at": datetime.now().strftime("%d %b %Y, %H:%M"),
            "source":   "manual"
        })
        return jsonify({"success": True, "count": len(stats["notes"])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-notes", methods=["POST"])
def get_notes():
    try:
        return jsonify({"success": True, "notes": get_stats(request.json.get("username","Student"))["notes"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete-note", methods=["POST"])
def delete_note():
    try:
        data  = request.json
        stats = get_stats(data.get("username", "Student"))
        i     = int(data.get("index", -1))
        if 0 <= i < len(stats["notes"]):
            stats["notes"].pop(i)
        return jsonify({"success": True, "notes": stats["notes"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-dashboard", methods=["POST"])
def get_dashboard():
    try:
        username = request.json.get("username", "Student")
        stats    = get_stats(username)
        leaderboard = sorted([
            {
                "name":      u,
                "questions": d["questions"],
                "sessions":  d["study_sessions"],
                "quizzes":   len(d["quiz_scores"]),
                "avg_score": round(sum(q["pct"] for q in d["quiz_scores"]) / len(d["quiz_scores"])) if d["quiz_scores"] else 0
            }
            for u, d in user_stats.items()
        ], key=lambda x: x["questions"] + x["sessions"] * 5, reverse=True)[:10]
        return jsonify({
            "success": True,
            "stats": {
                "questions":      stats["questions"],
                "study_sessions": stats["study_sessions"],
                "notes_count":    len(stats["notes"]),
                "quiz_scores":    stats["quiz_scores"],
                "joined_at":      stats["joined_at"],
                "avg_quiz":       round(sum(q["pct"] for q in stats["quiz_scores"]) / len(stats["quiz_scores"])) if stats["quiz_scores"] else 0
            },
            "leaderboard": leaderboard
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/record-quiz-score", methods=["POST"])
def record_quiz_score():
    try:
        data  = request.json
        get_stats(data.get("username","Student"))["quiz_scores"].append({
            "topic": data.get("topic","Quiz"), "score": data.get("score",0),
            "total": data.get("total",0),      "pct":   data.get("pct",0),
            "date":  datetime.now().strftime("%d %b")
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/record-session", methods=["POST"])
def record_session():
    try:
        username = request.json.get("username", "Student")
        stats    = get_stats(username)
        stats["study_sessions"] += 1
        return jsonify({"success": True, "sessions": stats["study_sessions"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear-chat", methods=["POST"])
def clear_chat():
    try:
        global chat_history
        chat_history = []
        username = request.json.get("username", "Student")
        # Broadcast clear event to all connected clients
        socketio.emit("chat_cleared", {"by": username})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Socket Events ─────────────────────────────────────

@socketio.on("connect")
def on_connect():
    print(f"Connected: {request.sid}")

@socketio.on("disconnect")
def on_disconnect():
    if request.sid in active_users:
        username = active_users.pop(request.sid)
        emit("user_left", {"username": username, "active_count": len(active_users)}, broadcast=True)

@socketio.on("join")
def on_join(data):
    username = data.get("username", "Student")
    active_users[request.sid] = username
    get_stats(username)
    emit("chat_history", {"messages": chat_history[-50:]})
    emit("user_joined", {"username": username, "active_count": len(active_users)}, broadcast=True)
    emit("active_users", {"users": list(active_users.values())})

@socketio.on("send_message")
def on_message(data):
    username = active_users.get(request.sid, "Unknown")
    message  = data.get("message", "").strip()
    if not message:
        return
    timestamp = datetime.now().strftime("%H:%M")
    msg_obj   = {"type": "user", "username": username, "message": message,
                 "timestamp": timestamp, "sid": request.sid}
    chat_history.append(msg_obj)
    emit("new_message", msg_obj, broadcast=True)

    if (message.lower().startswith("@bot")
            or message.lower().startswith("bot,")
            or message.strip().endswith("?")):
        emit("bot_typing", {"typing": True}, broadcast=True)
        try:
            get_stats(username)["questions"] += 1
            query     = message.replace("@bot","").replace("bot,","").strip() or message
            bot_reply = groq_ask(query)
            bot_msg   = {"type": "bot", "username": "StudyBot", "message": bot_reply,
                         "timestamp": datetime.now().strftime("%H:%M"), "sid": "bot"}
            chat_history.append(bot_msg)
            emit("bot_typing", {"typing": False}, broadcast=True)
            emit("new_message", bot_msg, broadcast=True)
        except Exception as e:
            emit("bot_typing", {"typing": False}, broadcast=True)
            emit("new_message", {"type": "bot", "username": "StudyBot",
                 "message": f"⚠️ {e}",
                 "timestamp": datetime.now().strftime("%H:%M"), "sid": "bot"}, broadcast=True)

@socketio.on("ask_bot")
def on_ask_bot(data):
    username = active_users.get(request.sid, "Student")
    question = data.get("question", "").strip()
    subject  = data.get("subject", "General")
    if not question:
        return
    get_stats(username)["questions"] += 1
    user_msg = {"type": "user", "username": username,
                "message": f"[{subject}] {question}",
                "timestamp": datetime.now().strftime("%H:%M"), "sid": request.sid}
    chat_history.append(user_msg)
    emit("new_message", user_msg, broadcast=True)
    emit("bot_typing", {"typing": True}, broadcast=True)
    try:
        bot_reply = groq_ask(f"Subject: {subject}\nQuestion: {question}")
        bot_msg   = {"type": "bot", "username": "StudyBot", "message": bot_reply,
                     "timestamp": datetime.now().strftime("%H:%M"), "sid": "bot"}
        chat_history.append(bot_msg)
        emit("bot_typing", {"typing": False}, broadcast=True)
        emit("new_message", bot_msg, broadcast=True)
    except Exception as e:
        emit("bot_typing", {"typing": False}, broadcast=True)
        emit("error", {"message": str(e)})

# ── Gunicorn entry point (Render production) ─────────
socketio_app = socketio.middleware(app)

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        print("Run: set GROQ_API_KEY=gsk_xxxxxxxxxxxx")
        exit(1)
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    debug = os.environ.get("RENDER") is None  # debug=False on Render, True locally
    print("\n" + "=" * 55)
    print("  StudyChat — Groq Llama 3.3 (FREE FOREVER)")
    print(f"  Running on port {port} | debug={debug}")
    print("=" * 55 + "\n")
    socketio.run(app, debug=debug, host="0.0.0.0", port=port)