import streamlit as st
from logic import load_all_knowledge, get_ai_response

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مساعد طويق الذكي", page_icon="🎓")
st.title("Tuwaiq Academy Assistant 🤖")

# --- 1. ضع مفتاح API الخاص بك هنا ---
DEEPSEEK_API_KEY = ""

# --- تحضير البيانات ---
@st.cache_data(ttl=1800)
def get_cached_context():
    return load_all_knowledge()

data_context = get_cached_context()

# --- القائمة الجانبية (شكل فقط) ---
with st.sidebar:
    st.image("https://tuwaiq.edu.sa/img/logos/logo.svg", width=150)
    st.info("البيانات محدثة من موقع الأكاديمية الرسمي.")
    if st.button("تحديث البيانات"):
        st.cache_data.clear()
        st.rerun()

# --- نظام المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الشات القديم
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# استقبال السؤال
if prompt := st.chat_input("كيف أقدر أخدمك بخصوص أكاديمية طويق؟"):
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد رد المساعد
    with st.chat_message("assistant"):
        with st.spinner("جاري مراجعة البيانات..."):
            try:
                # تحويل الرسايل للصيغة اللي يفهمها المودل
                formatted_messages = [
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages
                ]
                
                # إرسال المفتاح الثابت للدالة
                answer = get_ai_response(DEEPSEEK_API_KEY, formatted_messages, data_context)
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"حدث خطأ: {e}")