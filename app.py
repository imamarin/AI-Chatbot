import streamlit as st
import requests
import time
from io import StringIO
from textblob import TextBlob
# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Pengaturan")
api_key = st.sidebar.text_input("🔑 OpenRouter API Key", type="password")
model = st.sidebar.selectbox("🧠 Pilih Model",  ["mistralai/mistral-7b-instruct:free", "meta-llama/llama-3.1-70b-instruct"])
temperature = st.sidebar.slider("🔥 Temperature", 0.0, 1.0, 0.7)

# Tombol hapus riwayat
if st.sidebar.button("🗑️ Hapus Riwayat Chat"):
    st.session_state[f"messages_{model}"] = []

# ---------- TITLE ----------
st.title("🤖 Kenan AI Chatbot Bubble Style")
st.caption("Streamlit + OpenRouter API with Enhanced Features")

# ---------- SESSION STATE ----------
if f"messages_{model}" not in st.session_state:
    st.session_state[f"messages_{model}"] = []

# ---------- FUNGSI API ----------
def get_openrouter_response(user_message, model, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {api_key}",
        # "HTTP-Referer": "https://yourdomain.com",  # ganti sesuai domain kamu
        "X-Title": "Kenan AI - Chatbot"
    }

    payload = {
        "model": f"{model}",
        "messages": st.session_state[f"messages_{model}"] + [{"role": "user", "content": user_message}],
        "temperature": temperature,
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, json=payload)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]
        return ai_reply
    except Exception as e:
        return f"❌ Terjadi kesalahan: {e}"

# ---------- TAMPILKAN CHAT ----------
for msg in st.session_state[f"messages_{model}"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- INPUT USER ----------
if prompt := st.chat_input("Ketik pesan..."):
    blob = TextBlob(prompt)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "😊 Positif"
    elif polarity < -0.1:
        sentiment = "😠 Negatif"
    else:
        sentiment = "😐 Netral"

    with st.chat_message("user"):
        st.markdown(f"{prompt}\n\n> **Sentimen:** {sentiment}")

    st.session_state[f"messages_{model}"].append({
        "role": "user",
        "content": f"{prompt}\n\n> **Sentimen:** {sentiment}"
    })

    if not api_key:
        ai_reply = "❗ Harap masukkan API Key di sidebar."
    else:
        with st.chat_message("ai"):
            with st.spinner("🤖 AI sedang mengetik..."):
                time.sleep(0.5)
                ai_reply = get_openrouter_response(prompt, model, temperature)
                st.markdown(ai_reply)

    st.session_state[f"messages_{model}"].append({"role": "ai", "content": ai_reply})

# ---------- EKSPOR CHAT ----------
if st.session_state[f"messages_{model}"]:
    chat_text = "\n\n".join([
        f"{'👤 User' if msg['role'] == 'user' else '🤖 AI'}:\n{msg['content']}"
        for msg in st.session_state[f"messages_{model}"]
    ])

    st.download_button("📥 Unduh Riwayat Chat", data=chat_text, file_name="riwayat_chat.txt", mime="text/plain")


