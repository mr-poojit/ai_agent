import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "https://ai-agent-usw3.onrender.com/chat")

# Page config
st.set_page_config(page_title="AI Chat", layout="centered")

# --- CSS Styling ---
st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        max-height: 70vh;
        padding: 1rem;
        margin-bottom: 120px;
    }
    .message-row {
        display: flex;
        align-items: flex-end;
        margin-bottom: 1rem;
    }
    .bot .bubble {
        background-color: #eee;
        color: #111;
        border-radius: 1rem 1rem 1rem 0;
        align-self: flex-start;
        margin-right: auto;
    }
    .user .bubble {
        background-color: #1e1e1e;
        color: white;
        border-radius: 1rem 1rem 0 1rem;
        align-self: flex-end;
        margin-left: auto;
    }
    .bubble {
        padding: 0.75rem 1rem;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.2);
    }
    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: #888;
        color: white;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 0.5rem;
    }
    .bot {
        flex-direction: row;
    }
    .user {
        flex-direction: row-reverse;
    }
    .chat-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #0e1117;
        padding: 1rem 2rem;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 style='text-align:center;'>AI Appointment Assistant</h1>", unsafe_allow_html=True)

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Display Chat Messages ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for role, msg in st.session_state.chat_history:
    bubble_class = "user" if role == "user" else "bot"
    avatar = "U" if role == "user" else "🤖"
    st.markdown(f"""
        <div class="message-row {bubble_class}">
            <div class="avatar">{avatar}</div>
            <div class="bubble">{msg}</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Chat Input Footer (Form) ---
with st.form(key="chat_form", clear_on_submit=True):
    st.markdown('<div class="chat-footer">', unsafe_allow_html=True)
    cols = st.columns([10, 1])
    user_input = cols[0].text_input("Your message", placeholder="Type your message...", label_visibility="collapsed")
    submitted = cols[1].form_submit_button("➤")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Message Submission ---
if submitted and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))

    try:
        res = requests.post(BACKEND_URL, json={"message": user_input}, timeout=30)
        res.raise_for_status()
        reply = res.json().get("response", "Sorry, no response")

        reply = re.sub(
          r"(https://www\.google\.com/calendar/event\?[^\s\]]+)",
          r'<a href="\1" target="_blank">📅 View Meeting</a>',
          reply
        )
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    st.session_state.chat_history.append(("bot", reply))
    st.rerun()
