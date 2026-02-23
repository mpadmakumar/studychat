# 🎓 StudyChat — AI-Powered Student Learning Hub

Real-time group chat platform with an AI study assistant, quiz generator, PDF analyzer, Pomodoro timer, notes saver, voice I/O, and student dashboard.

Built with **Python Flask + Socket.IO + Groq (Llama 3.3 70B) — 100% Free**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Real-time Group Chat** | Multiple students chat simultaneously via WebSockets |
| 🤖 **AI StudyBot** | Ask doubts with `@bot` or `?` — instant answers |
| 📄 **PDF Upload & Analysis** | Upload notes → AI summarizes + generates exam questions |
| 🧠 **Quiz Generator** | Any topic → MCQ quiz with explanations + score tracking |
| ⏱️ **Pomodoro Timer** | 25/5/15 min focus-break cycles with session tracking |
| 📝 **Notes Saver** | Save bot answers, download as .txt |
| 🔊 **Voice Input & Output** | Speak questions, hear answers (Tamil + English) |
| 📊 **Dashboard & Leaderboard** | Stats per student + room leaderboard |
| 🌐 **Tamil + English** | Ask in Tamil, get answers in Tamil |
| 🔐 **Auto Login** | Name saved in browser — no re-login on refresh |

---

## 🚀 Local Setup (Run on your Computer)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Free Groq API Key
1. Go to 👉 **https://console.groq.com**
2. Sign up (free, no credit card needed)
3. Click **API Keys → Create API Key**
4. Copy the key

### Step 3: Create `.env` File
Create a file named `.env` in the project folder:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Run
```bash
python app.py
```

### Step 5: Open Browser
```
http://localhost:5000
```

---

## 📱 Share with Other Students (Same WiFi)

If everyone is on the same WiFi (college/class):

**Step 1:** Find your computer's IP address
```bash
# Windows
ipconfig
# Look for: IPv4 Address e.g. 192.168.1.5

# Mac/Linux
ifconfig | grep inet
```

**Step 2:** Students open this in their phone browser:
```
http://192.168.1.5:5000
```
*(Replace with your actual IP)*

---

## 🌍 Host Online — Free Forever (Render.com)

Deploy once → anyone anywhere can access via link!

### Why Render.com?
- ✅ Free tier — no credit card
- ✅ WebSocket (Socket.IO) support
- ✅ Custom URL: `yourapp.onrender.com`
- ✅ Auto-deploy from GitHub

### Step 1: Create `.gitignore` (protect your API key!)
```
.env
__pycache__/
*.pyc
```

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "StudyChat v2"
git branch -M main
git remote add origin https://github.com/yourusername/studychat.git
git push -u origin main
```

### Step 3: Create `render.yaml` in project root
```yaml
services:
  - type: web
    name: studychat
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: GROQ_API_KEY
        sync: false
```

### Step 4: Deploy on Render
1. Go to 👉 **https://render.com** → Sign up with GitHub
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Set **Environment Variable**: `GROQ_API_KEY` = your key
5. Click **Deploy** — done! 🎉

Your app will be live at: `https://studychat.onrender.com`

### ⚠️ Fix Render Free Tier Sleep (15 min idle = sleep)

**Free Fix: UptimeRobot**
1. Go to 👉 **https://uptimerobot.com** → Sign up free
2. Click **Add New Monitor**
3. Type: **HTTP(s)** | URL: `https://yourapp.onrender.com`
4. Interval: **5 minutes** → Save

✅ Server stays awake 24/7 — completely free!

---

## 🤖 How to Use StudyBot

| Method | Example |
|--------|---------|
| `@bot` prefix | `@bot explain Newton's 3 laws` |
| End with `?` | `What is photosynthesis?` |
| Tamil | `@bot ஒளிச்சேர்க்கை என்றால் என்ன?` |
| Sidebar Ask panel | Select subject → type → Ask StudyBot |

---

## 📂 Project Structure

```
studychat/
├── app.py                  # Flask + Socket.IO backend
├── requirements.txt        # Python dependencies
├── .env                    # API key (never commit!)
├── .gitignore
├── render.yaml             # Render.com deploy config
├── templates/
│   └── index.html          # Full frontend
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.x, Flask |
| Real-time | Flask-SocketIO, WebSockets |
| AI Model | Llama 3.3 70B (via Groq) |
| AI Inference | Groq — Free (14,400 req/day) |
| PDF Processing | PDF.js (browser-side) |
| Voice | Web Speech API (browser-native) |
| Session | localStorage |
| Config | python-dotenv |

---

## ⚡ Groq Free Tier Limits

| Metric | Limit |
|--------|-------|
| Requests / minute | 30 RPM |
| Requests / day | 14,400 RPD |
| Model | Llama 3.3 70B |
| Cost | **$0 — Forever Free** |

> 30 students × 480 questions/day = comfortable ✅

---

## 🐛 Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `GROQ_API_KEY not set` | Create `.env` file with your key |
| `403 Cloudflare` | Already fixed — uses `requests` library |
| `eventlet` crash on Python 3.14 | Already fixed — uses `threading` mode |
| `429 Rate limit` | Auto-retry built-in — wait 1 min |
| Voice not working | Use Chrome or Edge browser |

---

## 👥 Who Can Use This?

- 🧑‍🎓 **Students** — Doubt clearing, quiz practice, group study
- 👨‍🏫 **Teachers** — Share notes, generate quizzes, track engagement
- 🏫 **Coaching Centers** — Batch study rooms, 24/7 AI support
- 👩‍💻 **Self-Learners** — Personal AI tutor, progress tracking

---

## 🤖 Built With AI

Developed with **Claude (Anthropic)** AI assistant.

| Tool | Role |
|------|------|
| 🛠️ Claude (Anthropic) | Development assistant |
| ⚡ Groq | Free AI inference platform |
| 🦙 Llama 3.3 70B (Meta) | Open source AI model |

---

*StudyChat v2.0 — Free Forever 🎓*