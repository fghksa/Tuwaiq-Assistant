import streamlit as st
import time
from tuwaiq_agent import agent_executor

# --- Page Configuration ---
st.set_page_config(page_title="مساعد طويق الذكي", page_icon="💜", layout="wide")

# --- Strong CSS for RTL Support and Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* Force all messages and paragraphs to align to the right */
    .stMarkdown, .stMarkdown p, [data-testid="stChatMessage"] {
        text-align: right !important;
        direction: rtl !important;
    }
    
    .main-title { text-align: center; color: #9b51e0; font-size: 2.5rem; font-weight: 800; }
    .sub-title { text-align: center; color: #a0a0a0; }

    [data-testid="stSidebar"] { direction: rtl; background-color: #161b22; }

    .stButton>button {
        width: 100%; border-radius: 10px; background-color: #1e222d;
        color: white; border: 1px solid #9b51e0;
    }
    
    /* Hide default avatars for a cleaner look */
    [data-testid="stChatMessageAvatarAssistant"], [data-testid="stChatMessageAvatarUser"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

def clean_res(text):
    """Clean the agent's output by removing common prefixes."""
    for p in ["الرد النهائي للمستخدم هو:", "الرد النهائي للمستخدم:", "الرد النهائي:", "Final Answer:"]:
        text = text.replace(p, "")
    return text.strip()

# --- User Interface (UI) Header ---
st.markdown('<h1 class="main-title">🤖 مساعد طويق الذكي</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">مساعدك الذكي في أكاديمية طويق</p>', unsafe_allow_html=True)

# --- Initialize Chat Session State ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Sidebar (Requested Features) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#9b51e0;'>⚙️ خيارات سريعة</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🔍 فلاتر المعسكرات")
    col1, col2 = st.columns(2)
    with col1:
        f_ai = st.button("🤖 ذكاء اصطناعي")
        f_web = st.button("🌐 تطوير الويب")
    with col2:
        f_sec = st.button("🛡️ أمن سيبراني")
        f_data = st.button("📊 علوم بيانات")

    st.divider()
    
    st.markdown("### 🔗 روابط سريعة")
    st.markdown("[🌐 الموقع الرسمي](https://tuwaiq.edu.sa/)")
    st.markdown("[🐦 حساب X](https://twitter.com/TuwaiqAcademy)")

    st.divider()
    
    # Download Chat History Option
    if st.session_state.messages:
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📄 تحميل المحادثة", chat_text, file_name="chat.txt")

    # Clear Chat Conversation
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- Request Handling Logic ---
user_query = None

# Handle quick filter button clicks
if f_ai: user_query = "أبي معسكرات الذكاء الاصطناعي"
if f_web: user_query = "وش فيه معسكرات ويب؟"
if f_sec: user_query = "أبحث عن معسكرات الأمن السيبراني"
if f_data: user_query = "أبي معسكرات علوم البيانات"

# Handle standard chat input
if prompt := st.chat_input("اسألني عن طويق..."): user_query = prompt

# Execute the Agent and display results
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("جاري المراجعة..."):
            try:
                # Invoke the LangChain agent executor
                res = agent_executor.invoke({"input": user_query})
                clean_output = clean_res(res["output"])
                st.markdown(clean_output)
                st.session_state.messages.append({"role": "assistant", "content": clean_output})
            except:
                st.error("عذراً، النظام مشغول حالياً.")