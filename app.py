import streamlit as st
import pandas as pd
from fpdf import FPDF
import hashlib
from datetime import datetime, timedelta
import os

SECRET = "SAAD7387"
SCHOOL_NAME = "MAULANA AZAD URDU HIGH SCHOOL & JUNIOR COLLEGE"
SCHOOL_ADDR = "DHAD, DIST. BULDHANA - 444701 | Phone: 9021222111"
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
        days = int(parts[0].replace("MAZAD",""))
        chk_real = hashlib.md5(f"{days}{SECRET}".encode()).hexdigest()[:4].upper()
        if parts[1] == chk_real: return days
    except: pass
    return None

def save_expiry(d):
    with open(EXPIRY_FILE, "w") as f: f.write(d.isoformat())
def load_expiry():
    if os.path.exists(EXPIRY_FILE):
        try: return datetime.fromisoformat(open(EXPIRY_FILE).read().strip()).date()
        except: pass
    return None

st.set_page_config(page_title="Maulana Azad", layout="wide")

if "expiry" not in st.session_state: st.session_state.expiry = load_expiry()
if "students" not in st.session_state: st.session_state.students = []
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None

def is_active():
    if st.session_state.expiry is None: st.session_state.expiry = load_expiry()
    return st.session_state.expiry and datetime.now().date() <= st.session_state.expiry

if not is_active():
    st.markdown(f"<h1 style='text-align:center; color:#1e3a5f'>{SCHOOL_NAME}</h1>", unsafe_allow_html=True)
    st.divider()
    st.error("🔒 Locked! Code dalo")
    c = st.text_input("Activation Code:")
    if st.button("Activate", type="primary", use_container_width=True):
        d = verify_code(c)
        if d:
            exp = datetime.now().date() + timedelta(days=d)
            st.session_state.expiry = exp
            save_expiry(exp)
            st.rerun()
        else: st.error("Galat Code")
    with st.expander("Admin - M Saad"):
        p = st.text_input("Password", type="password")
        if p == "Saad@786":
            dn = st.number_input("Days", 1, 3650, 30)
            if st.button("Generate"): st.code(generate_code(dn))
    st.stop()

st.sidebar.success(f"Active till {st.session_state.expiry}")
st.markdown(f"<h2 style='text-align:center; color:#1e3a5f'>{SCHOOL_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center'>{SCHOOL_ADDR}</p>", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("Student Add")
    with st.form("add", clear_on_submit=True):
        name = st.text_input("Naam*")
        gender = st.selectbox("Gender", ["MALE","FEMALE","OTHER"])
        cl = st.selectbox("Class", ["5","6","7","8","9","10","11","12"])
        per = st.number_input("Percentage", 0.0, 100.0, step=0.01)
        if st.form_submit_button("Add", use_container_width=True):
            if name.strip():
                st.session_state.students.append({"name":name.strip(),"gender":gender,"class":cl,"percentage":per})
                st.session_state.pdf_data = None
    if st.button("Delete All"):
        st.session_state.students=[]
        st.session_state.pdf_data=None
        st.rerun()

if st.session_state.students:
    df = pd.DataFrame(st.session_state.students).sort_values(by="percentage", ascending=False).reset_index(drop=True)
    st.dataframe(df, use_container_width=True)

    def create_pdf_bytes(data_list):
        pdf = FPDF('P','mm','A4')
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.set_fill_color(30,58,95)
        pdf.rect(0,0,210,32,'F')
        pdf.set_xy(0,9)
        pdf.set_font("Helvetica","B",12)
        pdf.set_text_color(255,255,255)
        pdf.cell(210,7,SCHOOL_NAME,align='C')
        pdf.set_xy(0,18)
        pdf.set_font("Helvetica","",9)
        pdf.cell(210,5,SCHOOL_ADDR,align='C')
        pdf.ln(28)
        pdf.set_fill_color(14,138,122)
        pdf.set_text_color(255,255,255)
        pdf.set_font("Helvetica","B",10)
        cw = [15, 85, 30, 20, 30]
        hd = ["SR.NO","NAME OF STUDENT","GENDER","CLASS","PERCENTAGE"]
        for i,h in enumerate(hd):
            pdf.cell(cw[i],10,h,border=1,align='C',fill=True)
        pdf.ln()
        pdf.set_font("Helvetica","",10)
        pdf.set_text_color(0,0,0)
        for idx, row in enumerate(data_list,1):
            if idx%2==0: pdf.set_fill_color(234,246,243)
            else: pdf.set_fill_color(255,255,255)
            pdf.cell(cw[0],9,str(idx),border=1,align='C',fill=True)
            pdf.cell(cw[1],9,row["name"].upper()[:38],border=1,align='L',fill=True)
            pdf.cell(cw[2],9,row["gender"],border=1,align='C',fill=True)
            pdf.cell(cw[3],9,str(row["class"]),border=1,align='C',fill=True)
            pdf.set_font("Helvetica","B",10)
            pdf.cell(cw[4],9,f"{row['percentage']:.2f} %",border=1,align='C',fill=True)
            pdf.ln()
            pdf.set_font("Helvetica","",10)
        pdf.set_y(-18)
        pdf.set_font("Helvetica","I",7)
        pdf.set_text_color(100,100,100)
        pdf.cell(0,10,f"Thank you! | {FOOTER_TEXT} | {datetime.now().strftime('%d-%m-%Y')}",align='C')
        return bytes(pdf.output())

    # FIX: Ek hi button se PDF banao aur download dikhao
    if st.button("📄 Royal PDF Banao", type="primary", use_container_width=True):
        sorted_list = sorted(st.session_state.students, key=lambda x: x["percentage"], reverse=True)
        st.session_state.pdf_data = create_pdf_bytes(sorted_list)
        st.success("✅ PDF Ready! Neeche se download karo")

    if st.session_state.pdf_data:
        st.download_button(
            label="⬇️ Royal PDF Download Karo - Click Here",
            data=st.session_state.pdf_data,
            file_name=f"Royal_Merit_List_{datetime.now().strftime('%d%m%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
else:
    st.info("Koi student nahi, sidebar se add karo.")