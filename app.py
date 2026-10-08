import streamlit as st
import pandas as pd
from fpdf import FPDF
import hashlib
from datetime import datetime, timedelta

# --- CONFIG ---
SECRET = "SAAD7387"
SCHOOL_NAME = "MAULANA AZAD URDU HIGH SCHOOL & JUNIOR COLLEGE"
SCHOOL_ADDR = "DHAD | Phone: 9021222111"
FOOTER_TEXT = "Thank you! | Powered by M Saad Software - 7387246146"

def generate_code(days):
    chk = hashlib.md5(f"{days}{SECRET}".encode()).hexdigest()[:4].upper()
    return f"MAZAD{days}-{chk}"

def verify_code(code):
    try:
        code = code.strip().upper()
        if not code.startswith("MAZAD"):
            return None
        parts = code.split("-")
        if len(parts) < 2:
            return None
        days_part = parts[0].replace("MAZAD", "")
        days = int(days_part)
        chk_input = parts[1]
        chk_real = hashlib.md5(f"{days}{SECRET}".encode()).hexdigest()[:4].upper()
        if chk_input == chk_real:
            return days
        return None
    except:
        return None

st.set_page_config(page_title="Maulana Azad School", layout="wide", page_icon="🏫")

if "expiry" not in st.session_state:
    st.session_state.expiry = None
if "students" not in st.session_state:
    st.session_state.students = []

def is_active():
    if st.session_state.expiry is None:
        return False
    return datetime.now().date() <= st.session_state.expiry

if not is_active():
    st.markdown(f"<h1 style='text-align:center; color:#1e3a5f'>{SCHOOL_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center'>{SCHOOL_ADDR}</p>", unsafe_allow_html=True)
    st.divider()
    st.error("🔒 Software Locked Hai! Activation Code Dale")
    st.info("Code ke liye Contact Karo: M Saad - 7387246146")
    code_input = st.text_input("Activation Code Yaha Dale:", placeholder="Ex: MAZAD30-F4A2")
    if st.button("🔓 Activate Karo", use_container_width=True, type="primary"):
        days = verify_code(code_input)
        if days:
            st.session_state.expiry = datetime.now().date() + timedelta(days=days)
            st.success(f"Activated! {days} din ke liye. Expiry: {st.session_state.expiry}")
            st.balloons()
            st.rerun()
        else:
            st.error("Galat Code! Sahi code M Saad se lo.")
    with st.expander("🔑 Admin Login (Only for M Saad)"):
        pwd = st.text_input("Admin Password", type="password")
        if pwd == "Saad@786":
            st.success("Welcome Boss!")
            d = st.number_input("Kitne din ka code banana hai?", min_value=1, max_value=3650, value=30)
            if st.button("Code Banao"):
                c = generate_code(d)
                st.code(c)
        elif pwd!= "":
            st.error("Galat Password")
    st.stop()

days_left = (st.session_state.expiry - datetime.now().date()).days
st.sidebar.success(f"✅ Recharge Active: {days_left} din baaki")
st.sidebar.write(f"Expiry Date: {st.session_state.expiry}")
st.sidebar.divider()
st.markdown(f"<h2 style='text-align:center; color:#1e3a5f'>{SCHOOL_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center'>{SCHOOL_ADDR}</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("➕ Student Add Karo")
    with st.form("add_form"):
        name = st.text_input("Student ka Naam")
        gender = st.selectbox("Gender", ["MALE", "FEMALE", "OTHER"])
        class_name = st.selectbox("Class", ["5","6","7","8","9","10","11","12"])
        perc = st.number_input("Percentage", min_value=0.0, max_value=100.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button(" + Add Student", use_container_width=True)
        if submitted:
            if name.strip() == "":
                st.warning("Naam to dal bhai!")
            else:
                st.session_state.students.append({"name": name.strip(), "gender": gender, "class": class_name, "percentage": perc})
                st.success(f"{name} added!")
    if st.button("🗑️ Saare Students Delete Karo"):
        st.session_state.students = []
        st.rerun()

if st.session_state.students:
    df = pd.DataFrame(st.session_state.students)
    df = df.sort_values(by="percentage", ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    st.subheader(f"Total Students: {len(df)}")
    st.dataframe(df, use_container_width=True)
    def create_pdf(data):
        pdf = FPDF(orientation='L', format='A4')
        pdf.add_page()
        pdf.set_fill_color(30, 58, 95)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 15, SCHOOL_NAME, ln=True, align='C', fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, SCHOOL_ADDR, ln=True, align='C', fill=True)
        pdf.ln(10)
        pdf.set_fill_color(0, 150, 136)
        pdf.set_text_color(255,255,255)
        pdf.set_font("Arial", "B", 11)
        col_widths = [20, 110, 30, 20, 40]
        headers = ["SR. NO.", "NAME OF STUDENT", "GENDER", "CLASS", "PERCENTAGE"]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, h, border=1, align='C', fill=True)
        pdf.ln()
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", "", 10)
        for idx, row in enumerate(data, start=1):
            if idx % 2 == 0:
                pdf.set_fill_color(255,255,255)
            else:
                pdf.set_fill_color(236, 248, 248)
            pdf.cell(col_widths[0], 8, str(idx), border=1, align='C', fill=True)
            pdf.cell(col_widths[1], 8, row["name"], border=1, fill=True)
            pdf.cell(col_widths[2], 8, row["gender"], border=1, align='C', fill=True)
            pdf.cell(col_widths[3], 8, str(row["class"]), border=1, align='C', fill=True)
            pdf.set_text_color(0, 100, 80)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(col_widths[4], 8, f"{row['percentage']:.2f}%", border=1, align='C', fill=True)
            pdf.set_text_color(0,0,0)
            pdf.set_font("Arial", "", 10)
            pdf.ln()
        pdf.ln(10)
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(100,100,100)
        pdf.cell(0, 10, FOOTER_TEXT, align='C')
        return pdf
    if st.button("📄 Royal PDF Banao", type="primary", use_container_width=True):
        sorted_students = sorted(st.session_state.students, key=lambda x: x["percentage"], reverse=True)
        pdf = create_pdf(sorted_students)
        pdf_path = f"/tmp/Student_List_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button(label="⬇️ PDF Download Karo", data=f, file_name=f"Student_List_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
else:
    st.info("Abhi koi student add nahi hai. Sidebar se add karo.")