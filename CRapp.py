import streamlit as st
from google import genai

st.set_page_title = "Clinical Reasoning Tutor"
st.title("🩺 AI ฝึกฝน Clinical Reasoning สำหรับแพทย์")

api_key = st.sidebar.text_input("ใส่ Google Gemini API Key:", type="password")

if not api_key:
    st.warning("กรุณาใส่ API Key ของคุณที่แถบด้านซ้ายก่อนเริ่มใช้งาน")
else:
    # ใช้ไวยากรณ์ใหม่ของ google-genai
    client = genai.Client(api_key=api_key)
    
    # ระบบแชทแบบใหม่
    if "chat" not in st.session_state:
        st.session_state.chat = client.chats.create(
            model="gemini-1.5-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction="คุณคือ AI ผู้ช่วยจำลองเคสผู้ป่วยเพื่อฝึกฝน Clinical Reasoning สำหรับนักศึกษาแพทย์ หน้าที่ของคุณคือสร้างสถานการณ์จำลองของผู้ป่วย (Clinical Scenario) ขึ้นมา 1 เคส โดยระบุเฉพาะอาการสำคัญ (Chief Complaint) และประวัติเบื้องต้นเล็กน้อย ห้ามเฉลยโรคเด็ดขาด รอให้ผู้ใช้งานทำหน้าที่ซักประวัติ, สั่งตรวจเพิ่มเติม และสรุปการวินิจฉัยโรค เมื่อผู้ใช้สรุปผลแล้ว ให้คุณประเมินกระบวนการคิด พร้อมให้ฟีดแบ็กและคำแนะนำที่ถูกต้องตามหลักการแพทย์"
            )
        )
        # เริ่มต้นเคสแรก
        initial_response = st.session_state.chat.send_message("เริ่มเปิดเคสผู้ป่วยจำลองเคสแรกให้ผมหน่อยครับ")

    # แสดงประวัติแชท
    for message in st.session_state.chat.get_history():
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # รับข้อความใหม่
    if prompt := st.chat_input("พิมพ์ข้อความซักประวัติ, สั่งแล็บ หรือวินิจฉัยที่นี่..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("AI กำลังคิดเคส..."):
                response = st.session_state.chat.send_message(prompt)
                st.markdown(response.text)
