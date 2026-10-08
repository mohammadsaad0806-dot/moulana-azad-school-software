import streamlit as st
import pandas as pd
from fpdf import FPDF
import hashlib
from datetime import datetime, timedelta
import os

SECRET = "SAAD7387"
SCHOOL_NAME = "MAULANA AZAD URDU HIGH SCHOOL & JUNIOR COLLEGE"
SCHOOL_ADDR = "DHAD, DIST. WASHIM - 444701 | Phone: 9021222111"
FOOTER_TEXT = "Powered by M Saad Software - 7387246146"
EXPIRY_FILE = "expiry.txt"

def generate_code(days):
    chk = hashlib.md5(f"{days}{SECRET}".encode()).hexdigest()[:4].upper()
    return f"MAZAD{days}-{chk}"

def verify_code(code):
    try:
        code = code.strip().upper()
        if not code.startswith("MAZAD"): return None
        parts = code.split("-")
        if len(parts) < 2: return None
        days_part = parts[0].replace("MAZAD","")
        days = int(days_part)
        chk_input = parts[1]
        chk_real = hashlib.md5(f"{days}{SECRET}".encode()).hexdigest()[:4].upper()
        if chk_input == chk_real: return days
        return None
    except: return None

def save_expiry(date_obj):
    try:
        with open(EXPIRY_FILE, "w") as f:
            f.write(date_obj.isoformat())
    except: pass

def load_expiry():
    try:
        if os.path.exists(EXPIRY_FILE):
            with open(EXPIRY_FILE, "r") as f:
                d = f.read().strip()
                if d:
                    return datetime.fromisoformat(d).date()
    except: pass
    return None

st.set_page_config(page_title="Maulana Azad School", layout="wide", page_icon="🏫")

if "expiry" not in st.session_state:
    st.session_state.expiry = load_expiry()
if "students" not in st.session_state:
    st.session_state.students = []

def is_active():
    if st.session_state.expiry is None:
        st.session_state.expiry = load_expiry()
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
            expiry_date = datetime.now().date() + timedelta(days=days)
            st.session_state.expiry = expiry_date
            save_expiry(expiry_date)
            st.success(f"Activated! {days} din ke liye. Expiry: {expiry_date}")
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
                st.write(f"Ye code {d} din tak chalega")
        elif pwd!= "":
            st.error("Galat Password")
    st.stop()

days_left = (st.session_state.expiry - datetime.now().date()).days
st.sidebar.success(f"✅ Recharge Active: {days_left} din baaki | Expiry: {st.session_state.expiry}")
if st.sidebar.button("🔒 Logout / Lock Karo"):
    if os.path.exists(EXPIRY_FILE):
        os.remove(EXPIRY_FILE)
    st.session_state.expiry = None
    st.rerun()

st.markdown(f"<h2 style='text-align:center; color:#1e3a5f'>{SCHOOL_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#555'>{SCHOOL_ADDR}</p>", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("➕ Student Add Karo")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Student ka Naam*")
        gender = st.selectbox("Gender", ["MALE", "FEMALE", "OTHER"])
        class_name = st.selectbox("Class", ["5","6","7","8","9","10","11","12"])
        perc = st.number_input("Percentage (%)", min_value=0.0, max_value=100.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button(" + Add Student", use_container_width=True)
        if submitted:
            if name.strip() == "":
                st.warning("Naam to dal bhai!")
            else:
                st.session_state.students.append({"name": name.strip(), "gender": gender, "class": class_name, "percentage": perc})
                st.success(f"{name} added!")
    if st.button("🗑️ Saare Students Delete Karo", use_container_width=True):
        st.session_state.students = []
        st.rerun()
    with st.expander("🔑 M Saad Code Generator"):
        pwd2 = st.text_input("Password", type="password", key="admin2")
        if pwd2 == "Saad@786":
            d2 = st.number_input("Din", min_value=1, max_value=3650, value=30, key="d2")
            if st.button("Generate", key="gen2"):
                st.code(generate_code(d2))

if st.session_state.students:
    df = pd.DataFrame(st.session_state.students)
    df = df.sort_values(by="percentage", ascending=False).reset_index(drop=True)
    df_display = df.copy()
    df_display.index = df_display.index + 1
    df_display.index.name = "SR.NO"
    st.subheader(f"Total Students: {len(df)} | Sorted by Percentage")
    st.dataframe(df_display, use_container_width=True)

    class RoyalPDF(FPDF):
        def header(self):
            self.set_fill_color(15, 23, 42)
            self.set_text_color(255,255,255)
            self.set_font("Arial", "B", 18)
            self.cell(0, 14, SCHOOL_NAME, ln=True, align='C', fill=True)
            self.set_font("Arial", "", 10)
            self.set_fill_color(30, 58, 95)
            self.cell(0, 8, SCHOOL_ADDR, ln=True, align='C', fill=True)
            self.set_font("Arial", "B", 12)
            self.set_fill_color(251, 191, 36)
            self.set_text_color(15,23,42)
            self.cell(0, 9, "STUDENT MERIT LIST - PERCENTAGE WISE", ln=True, align='C', fill=True)
            self.ln(4)
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.set_text_color(100,100,100)
            self.cell(0, 10, f"{FOOTER_TEXT} | Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')} | Page {self.page_no()}", align='C')

    def create_pdf(data):
        pdf = RoyalPDF(orientation='L', format='A4')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        col_widths = [20, 125, 30, 20, 35]
        headers = ["SR.NO", "STUDENT NAME", "GENDER", "CLASS", "PERCENTAGE"]
        pdf.set_fill_color(15, 23, 42)
        pdf.set_text_color(255,255,255)
        pdf.set_font("Arial", "B", 11)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 11, h, border=1, align='C', fill=True)
        pdf.ln()
        pdf.set_font("Arial", "", 11)
        for idx, row in enumerate(data, start=1):
            if idx == 1: pdf.set_fill_color(255, 243, 205)
            elif idx == 2: pdf.set_fill_color(228, 228, 231)
            elif idx == 3: pdf.set_fill_color(255, 228, 196)
            else:
                if idx % 2 == 0: pdf.set_fill_color(255,255,255)
                else: pdf.set_fill_color(241, 245, 249)
            pdf.set_text_color(0,0,0)
            pdf.cell(col_widths[0], 9, str(idx), border=1, align='C', fill=True)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(col_widths[1], 9, row["name"].upper(), border=1, fill=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(col_widths[2], 9, row["gender"], border=1, align='C', fill=True)
            pdf.cell(col_widths[3], 9, str(row["class"]), border=1, align='C', fill=True)
            per = row["percentage"]
            if per >= 75: pdf.set_text_color(16,185,129)
            elif per >= 60: pdf.set_text_color(37,99,235)
            else: pdf.set_text_color(220,38,38)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(col_widths[4], 9, f"{per:.2f} %", border=1, align='C', fill=True)
            pdf.ln()
            pdf.set_text_color(0,0,0)
            pdf.set_font("Arial", "", 11)
        return pdf

    if st.button("📄 Royal PDF Banao - Topper List Design", type="primary", use_container_width=True):
        sorted_students = sorted(st.session_state.students, key=lambda x: x["percentage"], reverse=True)
        pdf = create_pdf(sorted_students)
        pdf_path = f"/tmp/Royal_List_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button(label="⬇️ Royal PDF Download Karo", data=f, file_name=f"Royal_Merit_List_{datetime.now().strftime('%d-%m-%Y')}.pdf", mime="application/pdf", use_container_width=True)
        st.success("✅ Royal PDF Ready Hai!")
else:
    st.info("Abhi koi student add nahi hai. Sidebar se add karo.")