import streamlit as st
import google.generativeai as genai

# ตั้งค่าหน้าเว็บ
st.set_page_title_id = "Clinical Reasoning Tutor"
st.title("🩺 AI ฝึกฝน Clinical Reasoning สำหรับแพทย์")
st.write("แชทบอทจำลองเคสผู้ป่วยเพื่อฝึกทักษะการซักประวัติและวินิจฉัยโรค")

# ช่องใส่ API Key (เพื่อให้ใช้งานได้ หรือจะซ่อนไว้ใส่ในระบบ Cloud ก็ได้)
api_key = st.sidebar.text_input("ใส่ Google Gemini API Key:", type="password")

if not api_key:
    st.warning("กรุณาใส่ API Key ของคุณที่แถบด้านซ้ายก่อนเริ่มใช้งาน (รับคีย์ฟรีได้ที่ Google AI Studio)")
else:
    # ตั้งค่า Gemini
    genai.configure(api_key=api_key)
    
    # ใช้โมเดล Gemini ตัวล่าสุดที่เก่งและเร็ว
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="คุณคือ AI ผู้ช่วยจำลองเคสผู้ป่วยเพื่อฝึกฝน Clinical Reasoning สำหรับนักศึกษาแพทย์ หน้าที่ของคุณคือสร้างสถานการณ์จำลองของผู้ป่วย (Clinical Scenario) ขึ้นมา 1 เคส โดยระบุเฉพาะอาการสำคัญ (Chief Complaint) และประวัติเบื้องต้นเล็กน้อย ห้ามเฉลยโรคเด็ดขาด รอให้ผู้ใช้งานทำหน้าที่ซักประวัติ, สั่งตรวจเพิ่มเติม และสรุปการวินิจฉัยโรค เมื่อผู้ใช้สรุปผลแล้ว ให้คุณประเมินกระบวนการคิด พร้อมให้ฟีดแบ็กและคำแนะนำที่ถูกต้องตามหลักการแพทย์"
    )

    # เก็บประวัติการแชท
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # เริ่มต้นให้ AI เปิดเคสแรกทักทายผู้ใช้
        initial_response = model.generate_content("เริ่มเปิดเคสผู้ป่วยจำลองเคสแรกให้ผมหน่อยครับ")
        st.session_state.messages.append({"role": "assistant", "content": initial_response.text})

    # แสดงข้อความแชทเก่าทั้งหมด
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # รับข้อความใหม่จากผู้ใช้ผ่านช่องแชท
    if prompt := st.chat_input("พิมพ์ข้อความซักประวัติ, สั่งแล็บ หรือวินิจฉัยที่นี่..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ให้ AI ตอบกลับ
        with st.chat_message("assistant"):
            with st.spinner("AI กำลังคิดเคส..."):
                # ส่งประวัติแชททั้งหมดให้ AI จำบริบท
                chat = model.start_chat(history=[
                    {"role": m["role"] if m["role"] != "assistant" else "model", "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1]
                ])
                response = chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
