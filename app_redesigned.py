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


# ── HTML (Responsive Glassmorphism UI) ───────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>
  <title>J.A.R.V.I.S AI ⚡</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg-1: #c9d8ee;
      --bg-2: #dce8f5;
      --bg-3: #e8f0fa;
      --glass: rgba(255,255,255,0.55);
      --glass-strong: rgba(255,255,255,0.75);
      --glass-border: rgba(255,255,255,0.85);
      --glass-border-subtle: rgba(255,255,255,0.5);
      --user-bubble: #4f46e5;
      --user-bubble2: #6366f1;
      --bot-bubble: rgba(255,255,255,0.78);
      --bot-text: #1e293b;
      --user-text: #ffffff;
      --accent: #4f46e5;
      --accent-soft: rgba(79,70,229,0.12);
      --muted: #64748b;
      --hint: #94a3b8;
      --font-main: 'Outfit', sans-serif;
      --font-mono: 'Space Mono', monospace;
      --radius-lg: 24px;
      --radius-md: 16px;
      --radius-sm: 10px;
      --shadow-card: 0 8px 40px rgba(80,100,180,0.13), 0 2px 8px rgba(80,100,180,0.07);
      --shadow-bubble: 0 2px 10px rgba(79,70,229,0.25);
    }

    html, body {
      height: 100%;
      font-family: var(--font-main);
      background: linear-gradient(145deg, var(--bg-1) 0%, var(--bg-2) 50%, var(--bg-3) 100%);
      background-attachment: fixed;
    }

    /* Ambient blobs */
    body::before, body::after {
      content: '';
      position: fixed;
      border-radius: 50%;
      pointer-events: none;
      z-index: 0;
    }
    body::before {
      width: 500px; height: 500px;
      background: radial-gradient(circle, rgba(167,139,250,0.18) 0%, transparent 65%);
      top: -120px; left: -120px;
      animation: drift1 14s ease-in-out infinite alternate;
    }
    body::after {
      width: 380px; height: 380px;
      background: radial-gradient(circle, rgba(99,102,241,0.13) 0%, transparent 65%);
      bottom: -80px; right: -80px;
      animation: drift2 11s ease-in-out infinite alternate;
    }
    @keyframes drift1 { to { transform: translate(70px, 90px); } }
    @keyframes drift2 { to { transform: translate(-60px, -70px); } }

    /* ── LAYOUT ── */
    .app {
      position: relative;
      z-index: 1;
      display: flex;
      height: 100vh;
      height: 100dvh;
    }

    /* ── SIDEBAR (desktop) ── */
    .sidebar {
      width: 68px;
      background: var(--glass);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-right: 1px solid var(--glass-border-subtle);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 0 24px;
      gap: 8px;
      flex-shrink: 0;
    }

    .sidebar-logo {
      width: 38px; height: 38px;
      background: var(--user-bubble);
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      margin-bottom: 16px;
      box-shadow: 0 4px 14px rgba(79,70,229,0.35);
    }
    .sidebar-logo svg { width: 18px; height: 18px; fill: none; stroke: white; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

    .s-btn {
      width: 42px; height: 42px;
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer;
      border: none;
      background: transparent;
      transition: background 0.18s;
    }
    .s-btn:hover { background: rgba(255,255,255,0.65); }
    .s-btn.active { background: rgba(255,255,255,0.85); box-shadow: 0 2px 10px rgba(79,70,229,0.12); }
    .s-btn svg { width: 17px; height: 17px; fill: none; stroke: #5b78c4; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

    .sidebar-spacer { flex: 1; }
    .s-avatar {
      width: 36px; height: 36px; border-radius: 50%;
      background: linear-gradient(135deg, #a78bfa, #6366f1);
      display: flex; align-items: center; justify-content: center;
      font-weight: 600; font-size: 13px; color: white;
      cursor: pointer;
    }

    /* ── MAIN PANEL ── */
    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
      height: 100vh;
      height: 100dvh;
    }

    /* ── HEADER ── */
    .chat-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 20px;
      background: var(--glass);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--glass-border-subtle);
      flex-shrink: 0;
    }

    /* Mobile hamburger */
    .menu-btn {
      display: none;
      width: 36px; height: 36px;
      border-radius: 10px;
      background: rgba(255,255,255,0.6);
      border: 1px solid var(--glass-border);
      align-items: center; justify-content: center;
      cursor: pointer;
      flex-shrink: 0;
    }
    .menu-btn svg { width: 16px; height: 16px; fill: none; stroke: #5b78c4; stroke-width: 2; stroke-linecap: round; }

    .bot-orb {
      width: 40px; height: 40px;
      background: linear-gradient(135deg, #1a1a2e, #2d2b55);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
      box-shadow: 0 0 0 3px rgba(99,102,241,0.25), 0 0 0 6px rgba(99,102,241,0.08);
      animation: orb-pulse 3.5s ease infinite;
      position: relative;
    }
    @keyframes orb-pulse {
      0%,100% { box-shadow: 0 0 0 3px rgba(99,102,241,0.25), 0 0 0 6px rgba(99,102,241,0.08); }
      50%      { box-shadow: 0 0 0 5px rgba(99,102,241,0.2), 0 0 0 10px rgba(99,102,241,0.05); }
    }
    .bot-orb::after {
      content: '';
      position: absolute;
      bottom: 2px; right: 2px;
      width: 9px; height: 9px;
      background: #22c55e;
      border-radius: 50%;
      border: 2px solid white;
    }
    .bot-eyes { display: flex; gap: 5px; }
    .bot-eye { width: 6px; height: 6px; background: white; border-radius: 50%; }

    .header-info { flex: 1; min-width: 0; }
    .header-name {
      font-size: 15px; font-weight: 600;
      color: #1e293b; letter-spacing: 0.01em;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .header-sub {
      font-size: 11px; color: var(--muted);
      font-family: var(--font-mono);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }

    .model-pill {
      display: inline-flex; align-items: center; gap: 5px;
      background: rgba(79,70,229,0.1);
      border: 1px solid rgba(79,70,229,0.2);
      border-radius: 20px;
      padding: 4px 10px;
      font-size: 10px; font-family: var(--font-mono);
      color: #4f46e5;
      flex-shrink: 0;
      white-space: nowrap;
    }
    .model-pill-dot {
      width: 5px; height: 5px; border-radius: 50%;
      background: #22c55e;
      animation: blink 2.5s ease infinite;
    }
    @keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.35;} }

    .hdr-btn {
      width: 34px; height: 34px;
      border-radius: 10px;
      background: rgba(255,255,255,0.6);
      border: 1px solid var(--glass-border);
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; flex-shrink: 0;
      transition: background 0.15s;
    }
    .hdr-btn:hover { background: rgba(255,255,255,0.9); }
    .hdr-btn svg { width: 14px; height: 14px; fill: none; stroke: var(--muted); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

    /* ── MESSAGES ── */
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px 16px 12px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
    }
    .chat-messages::-webkit-scrollbar { width: 4px; }
    .chat-messages::-webkit-scrollbar-track { background: transparent; }
    .chat-messages::-webkit-scrollbar-thumb { background: rgba(100,116,139,0.25); border-radius: 4px; }

    .date-divider {
      text-align: center;
      font-size: 11px;
      color: var(--hint);
      font-family: var(--font-mono);
      margin: 4px 0;
    }

    .msg-row {
      display: flex;
      align-items: flex-end;
      gap: 9px;
      animation: slideUp 0.28s cubic-bezier(.25,.8,.25,1) both;
    }
    @keyframes slideUp {
      from { opacity:0; transform: translateY(14px); }
      to   { opacity:1; transform: translateY(0); }
    }
    .msg-row.user { flex-direction: row-reverse; }

    .msg-av {
      width: 28px; height: 28px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
      background: linear-gradient(135deg, #1a1a2e, #2d2b55);
      margin-bottom: 2px;
    }
    .msg-av-eyes { display: flex; gap: 3px; }
    .msg-av-eye { width: 4px; height: 4px; background: white; border-radius: 50%; }
    .msg-row.user .msg-av {
      background: linear-gradient(135deg, #a78bfa, #6366f1);
      font-size: 11px; font-weight: 600; color: white;
    }

    .bubble-wrap { display: flex; flex-direction: column; max-width: 75%; }
    .msg-row.user .bubble-wrap { align-items: flex-end; }

    .bubble {
      padding: 10px 15px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.55;
      word-break: break-word;
      white-space: pre-wrap;
    }
    .msg-row.bot .bubble {
      background: var(--bot-bubble);
      color: var(--bot-text);
      border: 1px solid var(--glass-border);
      border-bottom-left-radius: 5px;
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }
    .msg-row.user .bubble {
      background: var(--user-bubble);
      color: var(--user-text);
      border-bottom-right-radius: 5px;
      box-shadow: var(--shadow-bubble);
    }

    .msg-time {
      font-size: 10px; color: var(--hint);
      margin-top: 4px; padding: 0 4px;
      font-family: var(--font-mono);
    }

    /* Typing indicator */
    .typing-indicator {
      display: none;
      align-items: flex-end;
      gap: 9px;
      animation: slideUp 0.28s both;
    }
    .typing-indicator.visible { display: flex; }
    .typing-bubble {
      background: var(--bot-bubble);
      border: 1px solid var(--glass-border);
      border-radius: 18px; border-bottom-left-radius: 5px;
      backdrop-filter: blur(10px);
      padding: 13px 17px;
      display: flex; gap: 5px; align-items: center;
    }
    .dot {
      width: 7px; height: 7px; border-radius: 50%;
      background: #94a3b8;
      animation: tdot 1.3s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes tdot {
      0%,60%,100% { transform: translateY(0); }
      30%          { transform: translateY(-7px); }
    }

    /* ── SUGGESTION CHIPS ── */
    .chips-row {
      display: flex; gap: 7px; flex-wrap: wrap;
      padding: 0 16px 10px;
      flex-shrink: 0;
    }
    .chip {
      background: var(--glass-strong);
      border: 1px solid var(--glass-border);
      border-radius: 20px;
      padding: 6px 13px;
      font-size: 12px; color: #475569;
      cursor: pointer;
      transition: all 0.18s;
      font-family: var(--font-main);
      white-space: nowrap;
    }
    .chip:hover { background: white; color: var(--accent); border-color: rgba(79,70,229,0.3); }

    /* ── INPUT AREA ── */
    .chat-input-area {
      padding: 10px 16px 16px;
      background: var(--glass);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-top: 1px solid var(--glass-border-subtle);
      flex-shrink: 0;
      padding-bottom: max(16px, env(safe-area-inset-bottom));
    }

    .input-row {
      display: flex;
      align-items: center;
      gap: 10px;
      background: var(--glass-strong);
      border: 1px solid var(--glass-border);
      border-radius: 18px;
      padding: 9px 9px 9px 16px;
      transition: border-color 0.2s, box-shadow 0.2s;
      box-shadow: 0 2px 12px rgba(80,120,200,0.07);
    }
    .input-row:focus-within {
      border-color: rgba(79,70,229,0.45);
      box-shadow: 0 0 0 3px rgba(79,70,229,0.08), 0 2px 12px rgba(80,120,200,0.07);
    }

    #userInput {
      flex: 1;
      background: none; border: none; outline: none;
      color: #1e293b;
      font-family: var(--font-main);
      font-size: 14px;
      line-height: 1.4;
      resize: none;
      max-height: 120px; min-height: 22px; height: 22px;
      overflow-y: auto;
    }
    #userInput::placeholder { color: var(--hint); }
    #userInput::-webkit-scrollbar { width: 0; }

    .send-btn {
      width: 38px; height: 38px;
      border-radius: 12px;
      border: none;
      background: var(--user-bubble);
      color: white;
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
      transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s, background 0.15s;
      box-shadow: 0 3px 14px rgba(79,70,229,0.38);
    }
    .send-btn:hover { background: #4338ca; transform: scale(1.06); box-shadow: 0 5px 18px rgba(79,70,229,0.48); }
    .send-btn:active { transform: scale(0.93); }
    .send-btn:disabled { opacity: 0.38; cursor: not-allowed; transform: none; }
    .send-btn svg { width: 15px; height: 15px; fill: none; stroke: white; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }

    .input-hint {
      text-align: center; font-size: 11px;
      color: var(--hint); margin-top: 8px;
      font-family: var(--font-mono);
    }

    /* ── MOBILE DRAWER SIDEBAR ── */
    .drawer-overlay {
      display: none;
      position: fixed; inset: 0; z-index: 50;
      background: rgba(15,12,41,0.35);
      backdrop-filter: blur(4px);
    }
    .drawer-overlay.open { display: block; }
    .drawer {
      position: fixed; left: 0; top: 0; bottom: 0; z-index: 51;
      width: 240px;
      background: rgba(230,238,250,0.96);
      backdrop-filter: blur(24px);
      border-right: 1px solid var(--glass-border);
      padding: 60px 16px 24px;
      transform: translateX(-100%);
      transition: transform 0.28s cubic-bezier(.25,.8,.25,1);
      display: flex; flex-direction: column; gap: 8px;
    }
    .drawer.open { transform: translateX(0); }
    .drawer-title {
      font-size: 11px; font-family: var(--font-mono);
      color: var(--hint); margin-bottom: 8px; padding: 0 4px;
      text-transform: uppercase; letter-spacing: 0.06em;
    }
    .drawer-item {
      display: flex; align-items: center; gap: 10px;
      padding: 10px 12px; border-radius: 12px;
      cursor: pointer; color: #334155; font-size: 14px;
      transition: background 0.15s;
    }
    .drawer-item:hover { background: rgba(255,255,255,0.7); }
    .drawer-item svg { width: 16px; height: 16px; fill: none; stroke: #5b78c4; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

    /* ── RESPONSIVE BREAKPOINTS ── */

    /* Large desktop: wider chat */
    @media (min-width: 1100px) {
      .main { max-width: 860px; margin: 0 auto; }
      .bubble-wrap { max-width: 65%; }
      .bubble { font-size: 15px; }
      .chips-row { padding: 0 24px 12px; }
      .chat-messages { padding: 24px 24px 12px; }
      .chat-input-area { padding: 12px 24px 20px; }
      .chat-header { padding: 16px 28px; }
    }

    /* Tablet */
    @media (max-width: 900px) {
      .sidebar { width: 60px; }
    }

    /* Mobile */
    @media (max-width: 640px) {
      .sidebar { display: none; }
      .menu-btn { display: flex; }
      .model-pill { display: none; }
      .hdr-btn { display: none; }
      .chat-header { padding: 12px 14px; }
      .chat-messages { padding: 14px 12px 10px; }
      .bubble { font-size: 14px; padding: 9px 13px; }
      .bubble-wrap { max-width: 82%; }
      .chips-row { padding: 0 12px 8px; overflow-x: auto; flex-wrap: nowrap; }
      .chip { flex-shrink: 0; }
      .chat-input-area { padding: 8px 12px 12px; padding-bottom: max(12px, env(safe-area-inset-bottom)); }
      .input-hint { display: none; }
    }

    @media (max-width: 380px) {
      .header-sub { display: none; }
      .bubble { font-size: 13.5px; }
    }
  </style>
</head>
<body>

<div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer">
  <div class="drawer-title">Navigation</div>
  <div class="drawer-item"><svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>Chat</div>
  <div class="drawer-item"><svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>History</div>
  <div class="drawer-item"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>Search</div>
  <div class="drawer-item"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>Settings</div>
</div>

<div class="app">
  <!-- Sidebar (desktop) -->
  <div class="sidebar">
    <div class="sidebar-logo">
      <svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
    </div>
    <button class="s-btn active" title="Chat">
      <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
    </button>
    <button class="s-btn" title="History">
      <svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
    </button>
    <button class="s-btn" title="Search">
      <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    </button>
    <div class="sidebar-spacer"></div>
    <div class="s-avatar" title="You">U</div>
  </div>

  <!-- Main -->
  <div class="main">
    <div class="chat-header">
      <button class="menu-btn" onclick="openDrawer()" aria-label="Menu">
        <svg viewBox="0 0 24 24"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <div class="bot-orb">
        <div class="bot-eyes"><div class="bot-eye"></div><div class="bot-eye"></div></div>
      </div>
      <div class="header-info">
        <div class="header-name">J.A.R.V.I.S AI ⚡</div>
        <div class="header-sub">llama-3.1 · groq cloud · online</div>
      </div>
      <div class="model-pill"><div class="model-pill-dot"></div>LLaMA 3.1</div>
      <div class="hdr-btn">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
      </div>
    </div>

    <div class="chat-messages" id="chatMessages">
      <div class="date-divider">Today</div>
      <div class="msg-row bot">
        <div class="msg-av"><div class="msg-av-eyes"><div class="msg-av-eye"></div><div class="msg-av-eye"></div></div></div>
        <div class="bubble-wrap">
          <div class="bubble">Good day. I am J.A.R.V.I.S — powered by LLaMA 3.1 via Groq. How can I assist you?</div>
          <div class="msg-time" id="initTime"></div>
        </div>
      </div>
      <div class="typing-indicator" id="typingIndicator">
        <div class="msg-av"><div class="msg-av-eyes"><div class="msg-av-eye"></div><div class="msg-av-eye"></div></div></div>
        <div class="typing-bubble">
          <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
      </div>
    </div>

    <div class="chips-row" id="chipsRow">
      <div class="chip" onclick="useChip(this)">Write code</div>
      <div class="chip" onclick="useChip(this)">Explain a concept</div>
      <div class="chip" onclick="useChip(this)">Analyze data</div>
      <div class="chip" onclick="useChip(this)">Draft an email</div>
      <div class="chip" onclick="useChip(this)">Summarize text</div>
    </div>

    <div class="chat-input-area">
      <div class="input-row">
        <textarea id="userInput" placeholder="Ask J.A.R.V.I.S anything…" rows="1"></textarea>
        <button class="send-btn" id="sendBtn">
          <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
      <div class="input-hint">Enter to send · Shift+Enter for new line</div>
    </div>
  </div>
</div>

<script>
  const chatMessages    = document.getElementById('chatMessages');
  const userInput       = document.getElementById('userInput');
  const sendBtn         = document.getElementById('sendBtn');
  const typingIndicator = document.getElementById('typingIndicator');
  const chipsRow        = document.getElementById('chipsRow');

  let history = [];
  let chipsUsed = false;

  document.getElementById('initTime').textContent = getTime();

  function getTime() {
    return new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
  }

  function openDrawer() {
    document.getElementById('drawer').classList.add('open');
    document.getElementById('drawerOverlay').classList.add('open');
  }
  function closeDrawer() {
    document.getElementById('drawer').classList.remove('open');
    document.getElementById('drawerOverlay').classList.remove('open');
  }

  function useChip(el) {
    userInput.value = el.textContent;
    userInput.focus();
    userInput.dispatchEvent(new Event('input'));
  }

  userInput.addEventListener('input', () => {
    userInput.style.height = '22px';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
  });

  function escapeHTML(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function hideChips() {
    if (!chipsUsed) { chipsUsed = true; chipsRow.style.display = 'none'; }
  }

  function addMessage(text, sender) {
    const row = document.createElement('div');
    row.className = 'msg-row ' + sender;
    const avHTML = sender === 'bot'
      ? '<div class="msg-av"><div class="msg-av-eyes"><div class="msg-av-eye"></div><div class="msg-av-eye"></div></div></div>'
      : '<div class="msg-av">U</div>';
    row.innerHTML = avHTML + '<div class="bubble-wrap"><div class="bubble">' + escapeHTML(text) + '</div><div class="msg-time">' + getTime() + '</div></div>';
    chatMessages.insertBefore(row, typingIndicator);
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
  }

  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    hideChips();
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
      const replyText = data.reply || '⚠️ No response received.';
      history.push({ role: 'user', content: text });
      history.push({ role: 'assistant', content: replyText });
      typingIndicator.classList.remove('visible');
      addMessage(replyText, 'bot');
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
