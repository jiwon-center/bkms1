import streamlit as st
import httpx

st.set_page_config(page_title="Mental Health Chatbot", layout="wide")
st.title("🧠 Cognitive Distortion Reframing Assistant")

API_URL = "http://localhost:8000/api/query_explanation"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력 받기
situation = st.text_input("What is the situation?")
thought = st.text_input("What thought did you have?")

if st.button("Send"):
    if not situation or not thought:
        st.warning("Please fill in both fields.")
    else:
        user_message = f"**Situation:** {situation}\n**Thought:** {thought}"
        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)

        payload = {"situation": situation, "thought": thought}
        try:
            resp = httpx.post(API_URL, json=payload, timeout=30.0)
            resp.raise_for_status()
            answer = resp.json()["response"]
        except Exception as e:
            answer = f"⚠️ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)