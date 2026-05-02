"""
J.A.R.V.I.S AI — Flask + Groq (LLaMA 3)
-----------------------------------------
Deploy-ready version. No Ollama or Gradio needed.

Local run:
    pip install flask groq
    set GROQ_API_KEY=your_key_here   (Windows)
    export GROQ_API_KEY=your_key_here  (Mac/Linux)
    python app.py

Then open:  http://localhost:7861
"""

import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Reply logic ───────────────────────────────────────────────────────────────
def reply(message: str, history: list) -> str:
    try:
        messages = []
        for msg in history:
            if "role" in msg and "content" in msg:
                messages.append({
                    "role": msg["role"],
                    "content": str(msg["content"])
                })
        messages.append({
            "role": "user",
            "content": str(message)
        })
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️  Error: {str(e)}"


# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>
  <title>J.A.R.V.I.S AI ⚡</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #dde8f5;
      --bg2: #e8f0fb;
      --surface: rgba(255,255,255,0.72);
      --surface-strong: rgba(255,255,255,0.88);
      --border: rgba(255,255,255,0.9);
      --border-soft: rgba(200,215,235,0.6);
      --user-msg: #3a35c8;
      --text-primary: #1a2035;
      --text-secondary: #5a6a85;
      --text-hint: #9aaabb;
      --accent: #3a35c8;
      --green: #34d399;
      --font: 'Inter', sans-serif;
    }

    html, body {
      height: 100%; width: 100%;
      font-family: var(--font);
      background: linear-gradient(160deg, #ccdaf0 0%, #dce8f8 40%, #e4eefa 70%, #d8e6f5 100%);
      background-attachment: fixed;
      overflow: hidden;
    }

    /* subtle animated blobs */
    .blob {
      position: fixed; border-radius: 50%;
      pointer-events: none; z-index: 0;
      filter: blur(60px); opacity: 0.55;
    }
    .blob1 {
      width: 420px; height: 420px;
      background: radial-gradient(circle, rgba(180,200,255,0.5), transparent 70%);
      top: -100px; left: -80px;
      animation: b1 15s ease-in-out infinite alternate;
    }
    .blob2 {
      width: 320px; height: 320px;
      background: radial-gradient(circle, rgba(160,180,255,0.35), transparent 70%);
      bottom: -60px; right: -60px;
      animation: b2 12s ease-in-out infinite alternate;
    }
    .blob3 {
      width: 200px; height: 200px;
      background: radial-gradient(circle, rgba(140,220,255,0.25), transparent 70%);
      top: 40%; left: 60%;
      animation: b1 18s ease-in-out infinite alternate-reverse;
    }
    @keyframes b1 { to { transform: translate(60px, 80px); } }
    @keyframes b2 { to { transform: translate(-50px, -60px); } }

    /* ── LAYOUT ── */
    .app {
      position: relative; z-index: 1;
      display: flex; align-items: center; justify-content: center;
      height: 100vh; height: 100dvh;
      padding: 0;
    }

    /* ── CHAT CARD ── */
    .chat-card {
      width: 100%; max-width: 440px;
      height: 100vh; height: 100dvh;
      display: flex; flex-direction: column;
      background: rgba(255,255,255,0.38);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border-left: 1px solid var(--border);
      border-right: 1px solid var(--border);
      overflow: hidden;
    }

    /* tablet/desktop: floating card */
    @media (min-width: 600px) {
      .app { padding: 24px; }
      .chat-card {
        height: min(780px, 92vh);
        border-radius: 28px;
        border: 1px solid var(--border);
        box-shadow: 0 24px 80px rgba(80,110,180,0.18), 0 4px 16px rgba(80,110,180,0.1);
      }
    }

    @media (min-width: 1024px) {
      .chat-card { max-width: 480px; height: min(820px, 90vh); }
    }

    /* ── HEADER ── */
    .header {
      display: flex; align-items: center; gap: 13px;
      padding: 16px 20px;
      background: rgba(255,255,255,0.5);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--border-soft);
      flex-shrink: 0;
    }

    /* robot orb — matches inspiration closely */
    .orb-wrap {
      position: relative; flex-shrink: 0;
    }
    .orb {
      width: 44px; height: 44px;
      background: radial-gradient(circle at 35% 35%, #2a2a4a, #0d0d1e);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      box-shadow:
        0 0 0 3px rgba(100,130,255,0.35),
        0 0 0 7px rgba(100,130,255,0.1),
        inset 0 1px 2px rgba(255,255,255,0.15);
      animation: orb-ring 3s ease-in-out infinite;
    }
    @keyframes orb-ring {
      0%,100% { box-shadow: 0 0 0 3px rgba(100,130,255,0.35), 0 0 0 7px rgba(100,130,255,0.1), inset 0 1px 2px rgba(255,255,255,0.15); }
      50%      { box-shadow: 0 0 0 5px rgba(100,130,255,0.25), 0 0 0 12px rgba(100,130,255,0.06), inset 0 1px 2px rgba(255,255,255,0.15); }
    }
    .orb-eyes { display: flex; gap: 6px; }
    .orb-eye {
      width: 7px; height: 7px;
      background: #fff;
      border-radius: 50%;
      box-shadow: 0 0 4px rgba(255,255,255,0.8);
    }
    .orb-glow {
      position: absolute; bottom: -2px; left: 50%;
      transform: translateX(-50%);
      width: 32px; height: 10px;
      background: linear-gradient(90deg, #6366f1, #818cf8, #6366f1);
      border-radius: 50%;
      filter: blur(6px);
      opacity: 0.7;
    }
    .status-dot {
      position: absolute; bottom: 2px; right: 2px;
      width: 10px; height: 10px;
      background: var(--green);
      border-radius: 50%;
      border: 2px solid white;
      animation: pulse-dot 2.5s ease infinite;
    }
    @keyframes pulse-dot {
      0%,100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .header-info { flex: 1; min-width: 0; }
    .header-name {
      font-size: 15px; font-weight: 600;
      color: var(--text-primary);
      letter-spacing: -0.01em;
    }
    .header-sub {
      font-size: 11px; color: var(--text-secondary);
      margin-top: 1px;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }

    .header-badge {
      display: flex; align-items: center; gap: 5px;
      background: rgba(99,102,241,0.1);
      border: 1px solid rgba(99,102,241,0.2);
      border-radius: 20px; padding: 4px 10px;
      font-size: 10px; font-weight: 500;
      color: #4f46e5; flex-shrink: 0;
    }
    .badge-dot {
      width: 5px; height: 5px; border-radius: 50%;
      background: var(--green);
      animation: pulse-dot 2.5s ease infinite;
    }

    /* ── MESSAGES ── */
    .messages {
      flex: 1; overflow-y: auto;
      padding: 20px 18px 10px;
      display: flex; flex-direction: column;
      gap: 10px;
      scroll-behavior: smooth;
    }
    .messages::-webkit-scrollbar { width: 3px; }
    .messages::-webkit-scrollbar-thumb { background: rgba(120,140,180,0.2); border-radius: 4px; }

    .date-label {
      text-align: center; font-size: 11px;
      color: var(--text-hint); margin: 4px 0 6px;
    }

    .row {
      display: flex; align-items: flex-end; gap: 8px;
      animation: rise 0.25s cubic-bezier(.25,.8,.25,1) both;
    }
    @keyframes rise {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .row.user { flex-direction: row-reverse; }

    /* small bot avatar in messages */
    .msg-orb {
      width: 30px; height: 30px; flex-shrink: 0;
      background: radial-gradient(circle at 35% 35%, #2a2a4a, #0d0d1e);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 0 0 2px rgba(100,130,255,0.3);
      margin-bottom: 2px;
    }
    .msg-orb-eyes { display: flex; gap: 4px; }
    .msg-orb-eye { width: 5px; height: 5px; background: white; border-radius: 50%; }

    .user-orb {
      width: 30px; height: 30px; flex-shrink: 0;
      background: linear-gradient(135deg, #818cf8, #6366f1);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 11px; font-weight: 600; color: white;
      margin-bottom: 2px;
    }

    .bwrap { display: flex; flex-direction: column; max-width: 78%; }
    .row.user .bwrap { align-items: flex-end; }

    .bubble {
      padding: 10px 14px;
      font-size: 14px; line-height: 1.55;
      word-break: break-word; white-space: pre-wrap;
    }
    .row.bot .bubble {
      background: var(--surface-strong);
      color: var(--text-primary);
      border-radius: 18px 18px 18px 5px;
      border: 1px solid var(--border);
      backdrop-filter: blur(12px);
    }
    .row.user .bubble {
      background: var(--user-msg);
      color: #fff;
      border-radius: 18px 18px 5px 18px;
      box-shadow: 0 4px 16px rgba(58,53,200,0.3);
    }

    .btime {
      font-size: 10px; color: var(--text-hint);
      margin-top: 4px; padding: 0 3px;
    }

    /* typing */
    .typing { display: none; align-items: flex-end; gap: 8px; animation: rise 0.25s both; }
    .typing.on { display: flex; }
    .typing-bub {
      background: var(--surface-strong);
      border: 1px solid var(--border);
      border-radius: 18px 18px 18px 5px;
      padding: 12px 16px;
      display: flex; gap: 5px; align-items: center;
    }
    .td {
      width: 7px; height: 7px; border-radius: 50%;
      background: #b0bcd0;
      animation: tdot 1.3s infinite ease-in-out;
    }
    .td:nth-child(2) { animation-delay: 0.18s; }
    .td:nth-child(3) { animation-delay: 0.36s; }
    @keyframes tdot {
      0%,60%,100% { transform: translateY(0); }
      30% { transform: translateY(-7px); }
    }

    /* ── CHIPS ── */
    .chips {
      display: flex; gap: 7px;
      padding: 4px 18px 10px;
      overflow-x: auto; flex-wrap: nowrap;
      flex-shrink: 0;
    }
    .chips::-webkit-scrollbar { display: none; }
    .chip {
      background: var(--surface-strong);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 12px; font-weight: 500;
      color: var(--text-secondary);
      cursor: pointer; white-space: nowrap;
      transition: all 0.18s;
      flex-shrink: 0;
    }
    .chip:hover {
      background: white; color: var(--accent);
      border-color: rgba(99,102,241,0.35);
      box-shadow: 0 2px 10px rgba(99,102,241,0.12);
    }

    /* ── INPUT ── */
    .input-area {
      padding: 8px 16px 16px;
      padding-bottom: max(16px, env(safe-area-inset-bottom));
      background: rgba(255,255,255,0.4);
      backdrop-filter: blur(20px);
      border-top: 1px solid var(--border-soft);
      flex-shrink: 0;
    }

    .input-box {
      display: flex; align-items: center; gap: 10px;
      background: var(--surface-strong);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 10px 10px 10px 18px;
      transition: border-color 0.2s, box-shadow 0.2s;
      box-shadow: 0 2px 14px rgba(80,110,180,0.07);
    }
    .input-box:focus-within {
      border-color: rgba(99,102,241,0.45);
      box-shadow: 0 0 0 3px rgba(99,102,241,0.08), 0 2px 14px rgba(80,110,180,0.07);
    }

    #userInput {
      flex: 1; border: none; outline: none; background: none;
      font-family: var(--font); font-size: 14px;
      color: var(--text-primary); line-height: 1.4;
      resize: none; height: 22px; max-height: 120px;
      overflow-y: auto;
    }
    #userInput::placeholder { color: var(--text-hint); }
    #userInput::-webkit-scrollbar { display: none; }

    .send-btn {
      width: 38px; height: 38px; flex-shrink: 0;
      border: none; border-radius: 13px;
      background: var(--accent);
      display: flex; align-items: center; justify-content: center;
      cursor: pointer;
      box-shadow: 0 3px 12px rgba(58,53,200,0.35);
      transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s;
    }
    .send-btn:hover { transform: scale(1.07); box-shadow: 0 5px 18px rgba(58,53,200,0.45); }
    .send-btn:active { transform: scale(0.92); }
    .send-btn:disabled { opacity: 0.35; cursor: not-allowed; transform: none; }
    .send-btn svg { width: 15px; height: 15px; }

    .input-hint {
      text-align: center; font-size: 10.5px;
      color: var(--text-hint); margin-top: 8px;
    }

    /* ── RESPONSIVE ── */
    @media (max-width: 599px) {
      .header { padding: 12px 16px; }
      .header-badge { display: none; }
      .messages { padding: 14px 14px 8px; }
      .chips { padding: 4px 14px 8px; }
      .input-area { padding: 8px 12px 12px; padding-bottom: max(12px, env(safe-area-inset-bottom)); }
      .input-hint { display: none; }
      .bubble { font-size: 13.5px; }
      .bwrap { max-width: 85%; }
    }

    @media (min-width: 600px) and (max-width: 1023px) {
      .chat-card { max-width: 420px; }
    }

    @media (min-width: 1024px) {
      .bubble { font-size: 14.5px; }
    }
  </style>
</head>
<body>
<div class="blob blob1"></div>
<div class="blob blob2"></div>
<div class="blob blob3"></div>

<div class="app">
  <div class="chat-card">

    <!-- Header -->
    <div class="header">
      <div class="orb-wrap">
        <div class="orb">
          <div class="orb-eyes">
            <div class="orb-eye"></div>
            <div class="orb-eye"></div>
          </div>
        </div>
        <div class="orb-glow"></div>
        <div class="status-dot"></div>
      </div>
      <div class="header-info">
        <div class="header-name">J.A.R.V.I.S AI ⚡</div>
        <div class="header-sub">LLaMA 3.1 · Groq Cloud · Online</div>
      </div>
      <div class="header-badge">
        <div class="badge-dot"></div>
        LLaMA 3.1
      </div>
    </div>

    <!-- Messages -->
    <div class="messages" id="messages">
      <div class="date-label">Today</div>
      <div class="row bot">
        <div class="msg-orb">
          <div class="msg-orb-eyes">
            <div class="msg-orb-eye"></div>
            <div class="msg-orb-eye"></div>
          </div>
        </div>
        <div class="bwrap">
          <div class="bubble">Good day. I am J.A.R.V.I.S — powered by LLaMA 3.1 via Groq. How can I assist you?</div>
          <div class="btime" id="initTime"></div>
        </div>
      </div>

      <!-- typing indicator stays at bottom -->
      <div class="typing" id="typing">
        <div class="msg-orb">
          <div class="msg-orb-eyes">
            <div class="msg-orb-eye"></div>
            <div class="msg-orb-eye"></div>
          </div>
        </div>
        <div class="typing-bub">
          <div class="td"></div><div class="td"></div><div class="td"></div>
        </div>
      </div>
    </div>

    <!-- Suggestion chips -->
    <div class="chips" id="chips">
      <div class="chip" onclick="useChip(this)">Write code</div>
      <div class="chip" onclick="useChip(this)">Explain a concept</div>
      <div class="chip" onclick="useChip(this)">Analyze data</div>
      <div class="chip" onclick="useChip(this)">Draft an email</div>
      <div class="chip" onclick="useChip(this)">Summarize text</div>
    </div>

    <!-- Input -->
    <div class="input-area">
      <div class="input-box">
        <textarea id="userInput" placeholder="Ask J.A.R.V.I.S anything…" rows="1"></textarea>
        <button class="send-btn" id="sendBtn">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
      <div class="input-hint">Enter to send &middot; Shift+Enter for new line</div>
    </div>

  </div>
</div>

<script>
  const msgsEl   = document.getElementById('messages');
  const inputEl  = document.getElementById('userInput');
  const sendBtn  = document.getElementById('sendBtn');
  const typing   = document.getElementById('typing');
  const chipsEl  = document.getElementById('chips');

  let history = [];
  let chipsHidden = false;

  document.getElementById('initTime').textContent = now();

  function now() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function hideChips() {
    if (!chipsHidden) { chipsHidden = true; chipsEl.style.display = 'none'; }
  }

  function useChip(el) {
    inputEl.value = el.textContent;
    inputEl.focus();
    autoResize();
  }

  function autoResize() {
    inputEl.style.height = '22px';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
  }

  inputEl.addEventListener('input', autoResize);

  function esc(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function addMsg(text, who) {
    const row = document.createElement('div');
    row.className = 'row ' + who;

    const avHTML = who === 'bot'
      ? `<div class="msg-orb"><div class="msg-orb-eyes"><div class="msg-orb-eye"></div><div class="msg-orb-eye"></div></div></div>`
      : `<div class="user-orb">U</div>`;

    row.innerHTML = avHTML + `
      <div class="bwrap">
        <div class="bubble">${esc(text)}</div>
        <div class="btime">${now()}</div>
      </div>`;

    msgsEl.insertBefore(row, typing);
    msgsEl.scrollTo({ top: msgsEl.scrollHeight, behavior: 'smooth' });
  }

  async function send() {
    const text = inputEl.value.trim();
    if (!text) return;
    hideChips();
    addMsg(text, 'user');
    inputEl.value = ''; autoResize();
    sendBtn.disabled = true;
    typing.classList.add('on');
    msgsEl.scrollTo({ top: msgsEl.scrollHeight, behavior: 'smooth' });

    try {
      const res  = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history })
      });
      const data = await res.json();
      const rep  = data.reply || '⚠️ No response received.';
      history.push({ role: 'user', content: text });
      history.push({ role: 'assistant', content: rep });
      typing.classList.remove('on');
      addMsg(rep, 'bot');
    } catch {
      typing.classList.remove('on');
      addMsg('⚠️ Could not reach the server.', 'bot');
    }

    sendBtn.disabled = false;
    inputEl.focus();
  }

  sendBtn.addEventListener('click', send);
  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });

  inputEl.focus();
</script>
</body>
</html>"""


# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data    = request.get_json(force=True)
    message = data.get('message', '')
    history = data.get('history', [])
    answer  = reply(message, history)
    return jsonify({'reply': answer})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7861))
    print(f"🧠 J.A.R.V.I.S AI starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False) 
