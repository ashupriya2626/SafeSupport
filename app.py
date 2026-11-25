import os
import json
import hashlib
import streamlit as st
from google import genai
from google.genai import types

# --- 1. CONFIGURATION & API SETUP ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
USERS_FILE = "users.json"

st.set_page_config(page_title="SafeSupport", page_icon="💜", layout="centered")

# Automatically find logo.jpg, logo.jpeg, or logo.png in the folder
LOGO_FILE = None
for filename in ["logo.jpg", "logo.jpeg", "logo.png"]:
    if os.path.exists(filename):
        LOGO_FILE = filename
        break

# --- 2. PASTEL PURPLE, BLUE & PINK THEME ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f3e8ff 0%, #e0f2fe 50%, #fce7f3 100%);
    color: #2e1065;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ede9fe 0%, #fce7f3 100%);
    border-right: 1px solid #e9d5ff;
}

.pastel-card {
    background-color: rgba(255, 255, 255, 0.82);
    border-radius: 20px;
    padding: 24px;
    border: 1px solid #e9d5ff;
    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.10);
    margin-bottom: 18px;
}

div[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.82);
    border-radius: 18px;
    padding: 12px 16px;
    border: 1px solid #e9d5ff;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.08);
    margin-bottom: 10px;
}

.safesupport-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #7c3aed, #2563eb, #db2777);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.stButton > button {
    background: linear-gradient(90deg, #a855f7, #3b82f6, #ec4899);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 10px 20px;
    font-weight: 600;
    width: 100%;
    transition: 0.2s ease;
}
.stButton > button:hover {
    opacity: 0.92;
    color: white;
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

SVG_LOGO = """
<svg width="64" height="64" viewBox="0 0 100 100" xmlns="http://w3.org">
  <defs>
    <linearGradient id="pastelGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#a855f7"/>
      <stop offset="50%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#ec4899"/>
    </linearGradient>
  </defs>
  <path d="M50 8 L86 22 V48 C86 71 70 88 50 94 C30 88 14 71 14 48 V22 L50 8 Z" fill="url(#pastelGrad)" opacity="0.9"/>
  <path d="M50 68 C50 68 31 55 31 42 C31 35 36 30 42 30 C46 30 49 32 50 35 C51 32 54 30 58 30 C64 30 69 35 69 42 C69 55 50 68 50 68 Z" fill="#ffffff"/>
</svg>
"""

# --- 3. SIMPLE ACCOUNT STORAGE (LOGIN / SIGN UP) ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# --- 4. SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "home"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi there! 👋 I'm **SafeSupport**. Whether you're stressed about board exams, feeling overwhelmed with assignments, or just having a tough day, I'm here to listen. What's on your mind?"
        }
    ]

def go_to(page_name: str):
    st.session_state.page = page_name
    st.rerun()

def render_header(subtitle: str = ""):
    col1, col2 = st.columns([1, 5])
    with col1:
        if LOGO_FILE:
            st.image(LOGO_FILE, width=72)
        else:
            st.markdown(SVG_LOGO, unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="safesupport-title">SafeSupport</div>', unsafe_allow_html=True)
        if subtitle:
            st.caption(subtitle)

# --- 5. SIDEBAR NAVIGATION (ONLY WHEN LOGGED IN) ---
if st.session_state.logged_in:
    with st.sidebar:
        if LOGO_FILE:
            st.image(LOGO_FILE, width=75)
        else:
            st.markdown(SVG_LOGO, unsafe_allow_html=True)
        st.markdown(f"### 👋 Hi, {st.session_state.username}!")
        st.divider()
        
        if st.button("🏠 Main Home"):
            go_to("home")
        if st.button("🎧 Explore Music & Podcasts"):
            go_to("explore")
        if st.button("💬 Talk to SafeSupport AI"):
            go_to("chatbot")
            
        st.divider()
        st.subheader("📞 24/7 Helplines")
        st.markdown("""
        * **Tele-MANAS:** `14416`
        * **Childline India:** `1098`
        * **Vandrevala:** `+91 9999 666 555`
        """)
        if st.button("🚪 Log Out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "home"
            st.rerun()

# =========================================================
# PAGE 1: LOGIN / SIGN UP PORTAL
# =========================================================
if not st.session_state.logged_in:
    render_header("Your safe, anonymous wellness space for Class 11 & 12 students.")
    st.markdown('<div class="pastel-card">', unsafe_allow_html=True)
    st.subheader("Welcome to SafeSupport 💜")
    st.write("Sign in to your account or create a free student profile to access calming resources and AI peer support.")

    tab_login, tab_signup = st.tabs(["🔑 Log In", "✨ Create Account"])

    with tab_login:
        with st.form("login_form"):
            login_user = st.text_input("Username or Nickname")
            login_pass = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            if submitted:
                users = load_users()
                if login_user in users and users[login_user]["password"] == hash_password(login_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = users[login_user]["name"]
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again or create a new account.")

    with tab_signup:
        with st.form("signup_form"):
            new_name = st.text_input("Display Name / Nickname (e.g., Alex)")
            new_user = st.text_input("Choose a Username")
            new_pass = st.text_input("Create a Password", type="password")
            created = st.form_submit_button("Create Account & Enter")
            if created:
                if not new_user or not new_pass or not new_name:
                    st.warning("Please fill out all fields.")
                else:
                    users = load_users()
                    if new_user in users:
                        st.error("That username is already taken. Try another one!")
                    else:
                        users[new_user] = {
                            "name": new_name,
                            "password": hash_password(new_pass)
                        }
                        save_users(users)
                        st.session_state.logged_in = True
                        st.session_state.username = new_name
                        st.session_state.page = "home"
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PAGE 2: MAIN WELCOME PAGE (WITH 2 NAVIGATION BUTTONS)
# =========================================================
elif st.session_state.page == "home":
    render_header("Student Mental Health & Wellness Portal")
    
    st.markdown(f"""
    <div class="pastel-card">
        <h2>✨ Welcome back, {st.session_state.username}!</h2>
        <h4>Take a deep breath. You are in a safe, judgment-free space.</h4>
        <p>Being in Class 11 and 12 comes with big exams, tough decisions, and heavy expectations. 
        Whether you want to unwind with calming music and inspiring podcasts or talk through what's stressing you out, choose where you'd like to start below:</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
        <div class="pastel-card">
            <h3>🎧 Explore Wellness</h3>
            <p>Listen to curated relaxing study music, guided meditations, and mental health podcasts for students.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Videos & Podcasts →"):
            go_to("explore")

    with col_right:
        st.markdown("""
        <div class="pastel-card">
            <h3>💬 SafeSupport AI Chat</h3>
            <p>Talk anonymously with our AI peer companion about exam stress, overwhelm, or anything on your mind.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open SafeSupport Chatbot →"):
            go_to("chatbot")

# =========================================================
# PAGE 3: EXPLORE PAGE (YOUTUBE PODCASTS & RELAXING MUSIC)
# =========================================================
elif st.session_state.page == "explore":
    render_header("Explore Calming Music & Student Podcasts")
    if st.button("← Back to Main Page"):
        go_to("home")

    st.markdown("### 🎵 Relaxing Meditation for Focus & Stress Relief")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**guided meditation 1**")
        st.video("https://youtu.be/HcSs5QAoBX4?si=FfKjvnstj-D6YFdV")
    with col2:
        st.markdown("**guided meditation 2**")
        st.video("https://youtu.be/xShv7mMmfW4?si=2wH3v3hEUQPzUdRA")

    st.divider()
    st.markdown("### 🎙️ Mental Health & Motivation Podcasts")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**how to cope with suicidal thoughts**")
        st.video("https://youtu.be/CAMAnPRLMH8?si=ReblXCii6RozS97-")
    with col4:
        st.markdown("**ways to cope with depression**")
        st.video("https://youtu.be/gyQX6bU1NIY?si=GRSOFGrLN-UWAZN1")

# =========================================================
# PAGE 4: AI CHATBOT PAGE
# =========================================================
elif st.session_state.page == "chatbot":
    render_header("Anonymous AI Peer Support Companion")
    
    top_col1, top_col2 = st.columns(2)
    with top_col1:
        if st.button("← Back to Main Page"):
            go_to("home")
    with top_col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # Safety & Crisis Layer
    CRISIS_KEYWORDS = [
        "suicide", "kill myself", "end my life", "want to die", "self-harm",
        "self harm", "cut myself", "hurt myself", "no reason to live",
        "better off dead", "end it all", "overdose", "hopeless"
    ]

    CRISIS_RESPONSE = """
### 💛 You Are Not Alone — Please Reach Out Right Now

It sounds like you are going through a really heavy time, and your safety matters most. Because SafeSupport is an AI school project, I cannot give you the care you deserve right now—**please talk to a real person who can help:**

* **School Counselor:** Visit **[Insert Counselor Name, Room #]** or speak to a trusted teacher right away.
* **Tele-MANAS (Govt. of India 24/7 Free Helpline):** Call **14416** or **1800-891-4416**
* **Childline India (24/7 Youth Support):** Call **1098**
* **Vandrevala Foundation (24/7 Call/WhatsApp):** **+91 9999 666 555**

You don't have to carry this alone. Please make that call or walk into the counselor's office now.
"""

    def check_for_crisis(user_text: str) -> bool:
        cleaned = user_text.lower()
        return any(keyword in cleaned for keyword in CRISIS_KEYWORDS)

    SYSTEM_PROMPT = f"""
You are SafeSupport, a warm, supportive, non-judgmental peer wellness companion talking to a student named {st.session_state.username} (Class 11 or 12).
Your role:
- Help students manage exam stress, board exam anxiety, study burnout, time management, peer pressure, and everyday low moods.
- Listen empathetically, validate their feelings, and ask gentle follow-up questions.
- Suggest simple, practical coping techniques like box breathing (4-4-4-4), the Pomodoro study method, journaling prompts, or breaking tasks into small steps.
- Keep responses concise, friendly, and easy to read (2 to 3 short paragraphs max).

Strict boundaries:
- You are NOT a doctor, psychologist, or therapist. Never diagnose mental health conditions or give medical advice.
- If a student mentions severe depression, trauma, abuse, or self-harm, gently encourage them to speak with their school counselor, parents, or a helpline.
"""

    @st.cache_data(ttl=300)
    def get_available_models(api_key: str):
        try:
            client = genai.Client(api_key=api_key)
            all_models = [
                m.name.replace("models/", "")
                for m in client.models.list()
                if "generateContent" in (m.supported_actions or [])
            ]
            preferred = [m for m in all_models if "flash" in m or "lite" in m or "gemma" in m]
            return preferred if preferred else all_models
        except Exception:
            return ["gemini-3.8-flash-lite", "gemini-3.8-flash"]

    bot_avatar = LOGO_FILE if LOGO_FILE else "💜"

    for msg in st.session_state.messages:
        avatar = bot_avatar if msg["role"] == "assistant" else "🧑‍🎓"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Share what's on your mind..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar=bot_avatar):
            if check_for_crisis(user_input):
                reply = CRISIS_RESPONSE
                st.error("Crisis Support Triggered")
                st.markdown(reply)
            else:
                client = genai.Client(api_key=API_KEY)
                conversation = [
                    types.Content(
                        role="user" if m["role"] == "user" else "model",
                        parts=[types.Part.from_text(text=m["content"])]
                    )
                    for m in st.session_state.messages[-6:]
                ]

                models_to_try = get_available_models(API_KEY)
                reply = None
                errors = []

                for model_name in models_to_try:
                    try:
                        placeholder = st.empty()
                        full_text = ""

                        if "gemma" in model_name:
                            gemma_convo = [
                                types.Content(
                                    role="user",
                                    parts=[types.Part.from_text(text=f"Instructions:\n{SYSTEM_PROMPT}")]
                                )
                            ] + conversation
                            stream = client.models.generate_content_stream(
                                model=model_name,
                                contents=gemma_convo,
                            )
                        else:
                            stream = client.models.generate_content_stream(
                                model=model_name,
                                contents=conversation,
                                config=types.GenerateContentConfig(
                                    system_instruction=SYSTEM_PROMPT,
                                    temperature=0.7,
                                )
                            )

                        for chunk in stream:
                            if chunk.text:
                                full_text += chunk.text
                                placeholder.markdown(full_text + "▌")

                        placeholder.markdown(full_text)
                        reply = full_text
                        break
                    except Exception as e:
                        errors.append(f"{model_name}: {e}")
                        continue

                if not reply:
                    reply = "⚠️ Could not get a reply. Details:\n\n" + "\n".join(errors[:2])
                    st.warning(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
