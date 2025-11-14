import streamlit as st
import time
import random
from utils import write_message
from agent import generate_response

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Celluloid", page_icon="Film", layout="centered")

# -------------------------------------------------
# FULL CSS – TOP LEFT & RIGHT FOOTER
# -------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top, #1d1d1d, #000000);
    }

    /* Title */
    .title-text {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        color: #ffdf70;
        text-shadow: 2px 2px #aa5500;
        margin-bottom: -10px;
    }

    .subtitle-text {
        text-align: center;
        font-size: 1.2rem;
        color: #cccccc;
        margin-bottom: 30px;
    }

    /* Chat Bubbles */
    .chat-bubble-user {
        background-color: #2b2b2b;
        color: white;
        padding: 12px 18px;
        border-radius: 15px;
        margin: 10px 0;
        width: fit-content;
        max-width: 75%;
        margin-left: auto;
    }

    .chat-bubble-assistant {
        background-color: #ffd54f;
        color: #333;
        padding: 12px 18px;
        border-radius: 15px;
        margin: 10px 0;
        width: fit-content;
        max-width: 75%;
    }

    /* ---------- TOP FIXED FOOTER (LEFT & RIGHT) ---------- */
    .top-footer {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 40px;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 16px;
        z-index: 999999;
        font-size: 0.85rem;
        color: orange;
        border-bottom: 1px solid rgba(255, 165, 0, 0.3);
    }

    .top-footer a {
        color: orange !important;
        font-weight: 700;
        text-decoration: none !important;
        white-space: nowrap;
    }

    .top-footer a:hover {
        text-decoration: underline !important;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .top-footer {
            font-size: 0.75rem;
            padding: 0 12px;
            height: 36px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# PAGE TITLE
# -------------------------------------------------
st.markdown(
    """
    <div class="title-text">Celluloid</div>
    <div class="subtitle-text">Ask me anything… except spoilers.</div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm your Movie Expert! How can I help you today?"}
    ]

# -------------------------------------------------
# TYPEWRITER EFFECT
# -------------------------------------------------
def typewriter(text: str):
    message = ""
    container = st.empty()
    for char in text:
        message += char
        container.markdown(f'<div class="chat-bubble-assistant">{message}</div>', unsafe_allow_html=True)
        time.sleep(0.01)

# -------------------------------------------------
# ENHANCED MESSAGE WRITER
# -------------------------------------------------
def write_ui_message(role: str, content: str):
    bubble = "chat-bubble-user" if role == "user" else "chat-bubble-assistant"
    st.markdown(f'<div class="{bubble}">{content}</div>', unsafe_allow_html=True)

# -------------------------------------------------
# SUBMIT HANDLER
# -------------------------------------------------
def handle_submit(message: str):
    with st.spinner("Thinking..."):
        response = generate_response(message)

    typewriter(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# -------------------------------------------------
# CHAT HISTORY DISPLAY
# -------------------------------------------------
for message in st.session_state.messages:
    write_ui_message(message["role"], message["content"])

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
if prompt := st.chat_input("What's on your mind?"):
    write_ui_message("user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    handle_submit(prompt)

# -------------------------------------------------
# RANDOM MOVIE QUOTE
# -------------------------------------------------
quotes = [
    "May the Force be with you.",
    "I'm gonna make him an offer he can't refuse.",
    "I'll be back.",
    "You talking to me?",
    "Why so serious?",
    "Roads? Where we're going, we don't need roads.",
]

st.markdown(
    f"<p style='text-align:center;color:#888;margin-top:40px;'>{random.choice(quotes)}</p>",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# TOP LEFT & RIGHT FOOTER
# -------------------------------------------------
st.markdown(
    """
    <div class="top-footer">
        <a href="https://www.linkedin.com/in/marina-ts-446939212/" target="_blank" rel="noopener noreferrer">
            Created by Marina TS
        </a>
        <a href="https://www.buymeacoffee.com/MarinaTS" target="_blank" rel="noopener noreferrer">
            Enjoying Celluloid? Buy me a coffee [coffee]
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)