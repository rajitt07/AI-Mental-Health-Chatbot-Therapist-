import streamlit as st
from auth import register_user, login_user
from openai import OpenAI
import os
from base64 import b64encode

st.set_page_config(page_title="AI Therapist", layout="centered")

# 🔹 Background image
IMAGE_PATH = "D:\Aurtherra Internship\WhatsApp Image 2025-04-18 at 15.30.57_05af7352.jpg"

def set_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded = b64encode(img_file.read()).decode()
    st.markdown(f"""
        <style>
        body {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .stApp {{
            background-color: rgba(0, 0, 0, 0.5);
            padding: 2rem;
            color: white;
        }}
        .bubble {{
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
            font-weight: 500;
        }}
        .user {{
            background-color: #d0eaff;
            color: #000;
            align-self: flex-end;
        }}
        .ai {{
            background-color: #f5f5f5;
            color: #000;
            align-self: flex-start;
        }}
        .stTextInput > div > div > input {{
            background-color: #2c2c2c;
            color: white;
            padding: 10px;
            border-radius: 8px;
        }}
        </style>
    """, unsafe_allow_html=True)

# 🔹 Apply background
set_background(IMAGE_PATH)

# 🔹 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# 🔹 Session state setup
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("chat_history", [])

# 🔹 Login / Signup UI
def login_ui():
    st.title("🧠 AI Therapist Login / Sign Up")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials.")
    
    with tab2:
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if register_user(new_user, new_pass):
                st.success("User registered! Please log in.")
            else:
                st.warning("Username already exists.")

# 🔹 Chat UI
def chat_ui():
    st.title(f"💬 Welcome, {st.session_state.username}")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.chat_history = []
        st.rerun()

    user_msg = st.text_input("Talk to your therapist:")
    if user_msg:
        st.session_state.chat_history.append(("You", user_msg))
        try:
            messages = [{"role": "system", "content": "You are a kind and empathetic AI therapist."}]
            for sender, msg in st.session_state.chat_history:
                role = "user" if sender == "You" else "assistant"
                messages.append({"role": role, "content": msg})
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {e}"
        st.session_state.chat_history.append(("Therapist", reply))

    # Display chat bubbles
    for sender, msg in st.session_state.chat_history:
        role = "user" if sender == "You" else "ai"
        st.markdown(f'<div class="bubble {role}"><b>{sender}:</b> {msg}</div>', unsafe_allow_html=True)

# 🔹 App Routing
chat_ui() if st.session_state.logged_in else login_ui()
