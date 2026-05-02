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


# ── HTML (Nova UI, styled as J.A.R.V.I.S) ────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>J.A.R.V.I.S AI</title>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg-from: #0f0c29;
      --bg-mid:  #302b63;
      --bg-to:   #24243e;
      --glass:   rgba(255,255,255,0.06);
      --glass-border: rgba(255,255,255,0.12);
      --user-bubble: linear-gradient(135deg,#6c63ff,#a78bfa);
      --bot-bubble: rgba(255,255,255,0.08);
      --bot-text: #e2e8f0;
      --user-text: #ffffff;
      --input-bg: rgba(255,255,255,0.07);
      --accent: #a78bfa;
      --accent2: #6ee7b7;
      --shadow: 0 8px 32px rgba(0,0,0,0.4);
      --radius-bubble: 20px;
      --font-main: 'Sora', sans-serif;
      --font-body: 'DM Sans', sans-serif;
    }

    body {
      font-family: var(--font-body);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, var(--bg-from) 0%, var(--bg-mid) 50%, var(--bg-to) 100%);
      overflow: hidden;
    }

    body::before, body::after {
      content: '';
      position: fixed;
      border-radius: 50%;
      filter: blur(80px);
      pointer-events: none;
      z-index: 0;
    }
    body::before {
      width: 400px; height: 400px;
      background: radial-gradient(circle, rgba(167,139,250,0.25) 0%, transparent 70%);
      top: -100px; left: -100px;
      animation: drift1 12s ease-in-out infinite alternate;
    }
    body::after {
      width: 300px; height: 300px;
      background: radial-gradient(circle, rgba(110,231,183,0.18) 0%, transparent 70%);
      bottom: -80px; right: -80px;
      animation: drift2 10s ease-in-out infinite alternate;
    }
    @keyframes drift1 { to { transform: translate(60px, 80px); } }
    @keyframes drift2 { to { transform: translate(-50px,-60px); } }

    .chat-window {
      position: relative;
      z-index: 1;
      width: min(480px, 96vw);
      height: min(720px, 92vh);
      display: flex;
      flex-direction: column;
      background: rgba(15,12,41,0.72);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--glass-border);
      border-radius: 28px;
      box-shadow: var(--shadow), 0 0 0 1px rgba(167,139,250,0.1) inset;
      overflow: hidden;
    }

    .chat-header {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 18px 22px;
      background: var(--glass);
      border-bottom: 1px solid var(--glass-border);
      flex-shrink: 0;
    }
    .avatar {
      width: 44px; height: 44px;
      border-radius: 50%;
      background: linear-gradient(135deg,#6c63ff,#a78bfa,#6ee7b7);
      display: flex; align-items: center; justify-content: center;
      font-size: 20px;
      box-shadow: 0 0 0 3px rgba(167,139,250,0.3);
      flex-shrink: 0;
      animation: pulse-ring 3s ease infinite;
    }
    @keyframes pulse-ring {
      0%,100% { box-shadow: 0 0 0 3px rgba(167,139,250,0.3); }
      50%      { box-shadow: 0 0 0 6px rgba(167,139,250,0.1); }
    }
    .header-info { flex: 1; }
    .header-info h1 {
      font-family: var(--font-main);
      font-size: 16px; font-weight: 600;
      color: #fff; letter-spacing: 0.3px;
    }
    .status {
      display: flex; align-items: center; gap: 6px;
      font-size: 12px; color: var(--accent2); margin-top: 2px;
      font-weight: 500;
    }
    .status-dot {
      width: 7px; height: 7px; border-radius: 50%;
      background: var(--accent2);
      animation: blink 2.5s ease infinite;
    }
    @keyframes blink {
      0%,100% { opacity:1; } 50% { opacity:0.4; }
    }

    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
    }
    .chat-messages::-webkit-scrollbar { width: 4px; }
    .chat-messages::-webkit-scrollbar-track { background: transparent; }
    .chat-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }

    .date-divider {
      text-align: center;
      font-size: 11px;
      color: rgba(255,255,255,0.3);
      font-family: var(--font-main);
      letter-spacing: 0.8px;
      text-transform: uppercase;
      margin: 4px 0;
    }

    .msg-row {
      display: flex;
      align-items: flex-end;
      gap: 10px;
      animation: slideUp 0.3s cubic-bezier(.25,.8,.25,1) both;
    }
    @keyframes slideUp {
      from { opacity:0; transform: translateY(18px); }
      to   { opacity:1; transform: translateY(0); }
    }
    .msg-row.user { flex-direction: row-reverse; }

    .msg-avatar {
      width: 30px; height: 30px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; flex-shrink: 0;
      background: linear-gradient(135deg,#6c63ff,#a78bfa);
    }
    .msg-row.user .msg-avatar {
      background: linear-gradient(135deg,#a78bfa,#6ee7b7);
    }

    .bubble-wrap { display: flex; flex-direction: column; max-width: 72%; }
    .msg-row.user .bubble-wrap { align-items: flex-end; }

    .bubble {
      padding: 11px 16px;
      border-radius: var(--radius-bubble);
      font-size: 14.5px;
      line-height: 1.55;
      word-break: break-word;
      white-space: pre-wrap;
    }
    .msg-row.bot .bubble {
      background: var(--bot-bubble);
      color: var(--bot-text);
      border: 1px solid var(--glass-border);
      border-bottom-left-radius: 5px;
    }
    .msg-row.user .bubble {
      background: var(--user-bubble);
      color: var(--user-text);
      border-bottom-right-radius: 5px;
      box-shadow: 0 4px 20px rgba(108,99,255,0.35);
    }

    .msg-time {
      font-size: 10.5px;
      color: rgba(255,255,255,0.3);
      margin-top: 5px;
      font-family: var(--font-main);
      padding: 0 4px;
    }

    .typing-indicator {
      display: none;
      align-items: flex-end;
      gap: 10px;
      animation: slideUp 0.3s both;
    }
    .typing-indicator.visible { display: flex; }
    .typing-bubble {
      background: var(--bot-bubble);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-bubble);
      border-bottom-left-radius: 5px;
      padding: 14px 18px;
      display: flex; gap: 5px; align-items: center;
    }
    .dot {
      width: 7px; height: 7px; border-radius: 50%;
      background: rgba(255,255,255,0.4);
      animation: bounce 1.3s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
      0%,60%,100% { transform: translateY(0); }
      30%          { transform: translateY(-8px); }
    }

    .chat-input-area {
      padding: 14px 16px 16px;
      background: var(--glass);
      border-top: 1px solid var(--glass-border);
      flex-shrink: 0;
    }
    .input-row {
      display: flex;
      align-items: center;
      gap: 10px;
      background: var(--input-bg);
      border: 1px solid var(--glass-border);
      border-radius: 50px;
      padding: 8px 8px 8px 18px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .input-row:focus-within {
      border-color: rgba(167,139,250,0.5);
      box-shadow: 0 0 0 3px rgba(167,139,250,0.1);
    }
    #userInput {
      flex: 1;
      background: none;
      border: none;
      outline: none;
      color: #fff;
      font-family: var(--font-body);
      font-size: 14.5px;
      line-height: 1.4;
      resize: none;
      max-height: 120px;
      min-height: 22px;
      height: 22px;
      overflow-y: auto;
    }
    #userInput::placeholder { color: rgba(255,255,255,0.28); }
    #userInput::-webkit-scrollbar { width: 0; }

    .send-btn {
      width: 40px; height: 40px;
      border-radius: 50%;
      border: none;
      background: linear-gradient(135deg, #6c63ff, #a78bfa);
      color: white;
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
      transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s;
      box-shadow: 0 4px 16px rgba(108,99,255,0.4);
    }
    .send-btn:hover { transform: scale(1.08); box-shadow: 0 6px 20px rgba(108,99,255,0.55); }
    .send-btn:active { transform: scale(0.94); }
    .send-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

    .input-hint {
      text-align: center;
      font-size: 11px;
      color: rgba(255,255,255,0.2);
      margin-top: 8px;
      font-family: var(--font-main);
    }

    @media (max-width: 520px) {
      .chat-window { border-radius: 20px; height: 95vh; }
      .bubble { font-size: 14px; }
    }
  </style>
</head>
<body>
<div class="chat-window">

  <div class="chat-header">
    <div class="avatar">🧠</div>
    <div class="header-info">
      <h1>J.A.R.V.I.S AI ⚡</h1>
      <div class="status">
        <span class="status-dot"></span>
        LLaMA 3.1 · Groq Cloud
      </div>
    </div>
  </div>

  <div class="chat-messages" id="chatMessages">
    <div class="date-divider">Today</div>
    <div class="msg-row bot">
      <div class="msg-avatar">🧠</div>
      <div class="bubble-wrap">
        <div class="bubble">Good day. I am J.A.R.V.I.S — powered by LLaMA 3.1 via Groq. How can I assist you?</div>
        <div class="msg-time" id="initTime"></div>
      </div>
    </div>
    <div class="typing-indicator" id="typingIndicator">
      <div class="msg-avatar">🧠</div>
      <div class="typing-bubble">
        <div class="dot"></div><div class="dot"></div><div class="dot"></div>
      </div>
    </div>
  </div>

  <div class="chat-input-area">
    <div class="input-row">
      <textarea id="userInput" placeholder="Ask J.A.R.V.I.S anything…" rows="1"></textarea>
      <button class="send-btn" id="sendBtn">
        <svg width="17" height="17" fill="none" viewBox="0 0 24 24">
          <path d="M22 2 11 13" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M22 2 15 22 11 13 2 9l20-7z" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    <div class="input-hint">Enter to send · Shift+Enter for new line</div>
  </div>

</div>

<script>
  const chatMessages    = document.getElementById('chatMessages');
  const userInput       = document.getElementById('userInput');
  const sendBtn         = document.getElementById('sendBtn');
  const typingIndicator = document.getElementById('typingIndicator');

  let history = [];

  document.getElementById('initTime').textContent = getTime();

  function getTime() {
    return new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
  }

  userInput.addEventListener('input', () => {
    userInput.style.height = '22px';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
  });

  function escapeHTML(str) {
    return str
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function addMessage(text, sender) {
    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;
    const icon = sender === 'bot' ? '🧠' : '👤';
    row.innerHTML = `
      <div class="msg-avatar">${icon}</div>
      <div class="bubble-wrap">
        <div class="bubble">${escapeHTML(text)}</div>
        <div class="msg-time">${getTime()}</div>
      </div>`;
    chatMessages.insertBefore(row, typingIndicator);
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
  }

  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    userInput.value = '';
    userInput.style.height = '22px';
    sendBtn.disabled = true;

    typingIndicator.classList.add('visible');
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history })
      });
      const data = await res.json();
      const reply = data.reply || '⚠️ No response received.';

      history.push({ role: 'user',      content: text  });
      history.push({ role: 'assistant', content: reply });

      typingIndicator.classList.remove('visible');
      addMessage(reply, 'bot');
    } catch (err) {
      typingIndicator.classList.remove('visible');
      addMessage('⚠️ Could not reach the server.', 'bot');
    }

    sendBtn.disabled = false;
    userInput.focus();
  }

  sendBtn.addEventListener('click', sendMessage);
  userInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  userInput.focus();
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
