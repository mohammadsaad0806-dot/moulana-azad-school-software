import streamlit as st
import pandas as pd
from fpdf import FPDF
import hashlib
from datetime import datetime, timedelta
import os
import json

SECRET = st.secrets.get("SECRET_KEY", "SAAD7387")
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "Saad@786")

SCHOOL_NAME = "MAULANA AZAD URDU HIGH SCHOOL & JUNIOR COLLEGE"
SCHOOL_ADDR = "DHAD, DIST. BULDHANA - 443106 | Phone: 9021222111"
FOOTER_TEXT = "Powered by M Saad Software - 7387246146"

EXPIRY_FILE = "expiry.txt"
STUDENTS_FILE = "students.json"

CLASSES = ["NUR", "LKG", "UKG", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
GENDERS = ["MALE", "FEMALE", "OTHER"]

def generate_code(days: int) -> str:
    chk = hashlib.md5(f"{days}{SECRET}".encode()).hexdigest()[:4].upper()
    return f"MAZAD{days}-{chk}"

def verify_code(code: str):
    try:
        code = code.strip().upper().replace(" ", "")
        if not code.startswith("MAZAD") or "-" not in code: return None
        parts = code.split("-")
        days = int(parts[0].replace("MAZAD", ""))
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

def save_students(students):
    try:
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=2)
    except: pass

def load_students():
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def get_division(per: float, pass_marks: float) -> str:
    if per < pass_marks: return "FAIL"
    if per >= 60: return "FIRST"
    if per >= 45: return "SECOND"
    return "THIRD"

def safe_name(name: str, limit: int = 32) -> str:
    n = name.upper()
    return n if len(n) <= limit else n[: limit - 3] + "..."

# ================= PDF - WITH RED FOR FAIL / GREEN FOR PASS =================
def create_pdf_bytes(data_list, pass_marks):
    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    pdf.set_fill_color(30, 58, 95)
    pdf.rect(0, 0, 210, 32, "F")
    pdf.set_xy(0, 9)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(210, 7, SCHOOL_NAME, align="C")
    pdf.set_xy(0, 18)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(210, 5, SCHOOL_ADDR, align="C")
    pdf.set_xy(0, 26)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(210, 4, f"Passing Criteria: {pass_marks:.0f}% | Merit List", align="C")
    pdf.ln(28)

    pdf.set_fill_color(14, 138, 122)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8.5)
    cw = [13, 65, 22, 16, 22, 24, 18]
    hd = ["RANK", "NAME OF STUDENT", "GENDER", "CLASS", "PERCENTAGE", "DIVISION", "REMARKS"]
    for i, h in enumerate(hd):
        pdf.cell(cw[i], 9, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8.5)
    for idx, row in enumerate(data_list, 1):
        per = float(row["percentage"])
        is_fail = per < pass_marks
        div = get_division(per, pass_marks)
        remark = "PASS" if not is_fail else "FAIL"

        # ===== FAIL = RED, PASS = GREEN TINT =====
        if is_fail:
            pdf.set_fill_color(255, 200, 200) # Light Red background
            pdf.set_text_color(180, 0, 0) # Dark Red text
        else:
            if idx % 2 == 0: pdf.set_fill_color(234, 246, 243) # Light Green
            else: pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0, 0, 0)

        pdf.cell(cw[0], 8, str(idx), border=1, align="C", fill=True)
        pdf.cell(cw[1], 8, safe_name(row["name"], 32), border=1, align="L", fill=True)
        pdf.cell(cw[2], 8, row["gender"], border=1, align="C", fill=True)
        pdf.cell(cw[3], 8, str(row["class"]), border=1, align="C", fill=True)

        # Percentage Bold
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(cw[4], 8, f"{per:.2f}%", border=1, align="C", fill=True)
        pdf.set_font("Helvetica", "", 8.5)

        pdf.cell(cw[5], 8, div, border=1, align="C", fill=True)

        # Remarks Bold + Color
        if is_fail:
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(180, 0, 0)
        else:
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(0, 128, 0) # Green for PASS

        pdf.cell(cw[6], 8, remark, border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_text_color(0,0,0)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 58, 95)
    total = len(data_list)
    passed = sum(1 for r in data_list if float(r["percentage"]) >= pass_marks)
    failed = total - passed
    pdf.cell(0, 6, f"Total: {total} | Passed: {passed} | Failed: {failed} | Passing: {pass_marks:.0f}%", align="L")

    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Thank you! | {FOOTER_TEXT} | {datetime.now().strftime('%d-%m-%Y')}", align="C")
    return bytes(pdf.output())

# ================= SETUP =================
st.set_page_config(page_title="Maulana Azad", layout="wide")

if "expiry" not in st.session_state: st.session_state.expiry = load_expiry()
if "students" not in st.session_state: st.session_state.students = load_students()
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None
if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = False
if "pass_marks" not in st.session_state: st.session_state.pass_marks = 33.0

def is_active():
    if st.session_state.expiry is None: st.session_state.expiry = load_expiry()
    today = datetime.now().date()
    return st.session_state.expiry and today <= st.session_state.expiry

if not is_active():
    st.markdown(f"<h1 style='text-align:center; color:#1e3a5f'>{SCHOOL_NAME}</h1>", unsafe_allow_html=True)
    st.divider()
    st.error("🔒 Locked! Activation Code daalo")
    c = st.text_input("Activation Code:")
    if st.button("Activate", type="primary", use_container_width=True):
        d = verify_code(c)
        if d:
            exp = datetime.now().date() + timedelta(days=d)
            st.session_state.expiry = exp
            save_expiry(exp)
            st.success(f"✅ Activated till {exp}"); st.rerun()
        else: st.error("❌ Galat Code")
    with st.expander("🔐 Admin - M Saad"):
        p = st.text_input("Password", type="password")
        if p == ADMIN_PASS:
            dn = st.number_input("Days", 1, 3650, 30)
            if st.button("Generate Code"): st.code(generate_code(dn))
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.success(f"✅ Active till {st.session_state.expiry}")
    days_left = (st.session_state.expiry - datetime.now().date()).days
    st.info(f"⏳ {days_left} din baaki")

    if st.button("🔒 Logout / Lock Karo", use_container_width=True):
        if os.path.exists(EXPIRY_FILE): os.remove(EXPIRY_FILE)
        st.session_state.expiry = None
        st.rerun()

    st.divider()

    # ===== NAYA FEATURE 1: FAIL KITNE % PAR? =====
    st.subheader("⚙️ Passing Settings")
    pass_input = st.number_input("Fail Kitne % se niche? (Passing Marks)", 0.0, 100.0, value=st.session_state.pass_marks, step=1.0)
    st.session_state.pass_marks = pass_input
    st.caption(f"👉 {pass_input:.0f}% se niche wala FAIL, uske upar PASS")
    st.divider()

    st.header("➕ Student Add")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Naam*")
        gender = st.selectbox("Gender", GENDERS)
        cl = st.selectbox("Class", CLASSES)
        per = st.number_input("Percentage", 0.0, 100.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Add Student", use_container_width=True)
        if submitted:
            if not name.strip(): st.warning("⚠️ Naam khaali nahi")
            else:
                dup = any(s["name"].strip().lower() == name.strip().lower() and s["class"] == cl for s in st.session_state.students)
                if dup: st.warning("⚠️ Already added hai")
                else:
                    st.session_state.students.append({"name": name.strip(),"gender": gender,"class": cl,"percentage": per})
                    save_students(st.session_state.students)
                    st.session_state.pdf_data = None
                    st.success(f"✅ {name} added")

    st.divider()
    with st.expander("🔑 M Saad Code Generator"):
        pwd2 = st.text_input("Admin Password", type="password", key="admin2")
        if pwd2 == ADMIN_PASS:
            st.success("Welcome Boss!")
            d2 = st.number_input("Kitne din ka code?", min_value=1, max_value=3650, value=30, key="d2")
            if st.button("Generate Code", key="gen2"):
                st.code(generate_code(d2))
        elif pwd2!= "":
            st.error("Galat Password")

    st.divider()
    if st.button("🗑️ Delete All Students", use_container_width=True):
        st.session_state.confirm_delete = True
    if st.session_state.confirm_delete:
        st.warning("⚠️ Pakka delete?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Haan", type="primary", use_container_width=True):
                st.session_state.students = []
                st.session_state.pdf_data = None
                st.session_state.confirm_delete = False
                save_students([])
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.confirm_delete = False
                st.rerun()

# ================= MAIN =================
st.markdown(f"<h2 style='text-align:center; color:#1e3a5f'>{SCHOOL_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center'>{SCHOOL_ADDR}</p>", unsafe_allow_html=True)
st.divider()

# Live Preview of Pass/Fail Logic
st.info(f"📊 Current Rule: **{st.session_state.pass_marks:.0f}% se kam = FAIL (Red)** | **{st.session_state.pass_marks:.0f}% ya usse zyada = PASS (Green)**")

if st.session_state.students:
    df = pd.DataFrame(st.session_state.students).sort_values(by="percentage", ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "RANK"
    df["STATUS"] = df["percentage"].apply(lambda x: "❌ FAIL" if x < st.session_state.pass_marks else "✅ PASS")
    df_show = df.rename(columns={"name": "NAME","gender": "GENDER","class": "CLASS","percentage": "PERCENTAGE"})
    st.subheader(f"📋 Total Students: {len(df)}")
    st.dataframe(df_show, use_container_width=True)

    if st.button("📄 Royal PDF Banao", type="primary", use_container_width=True):
        sorted_list = sorted(st.session_state.students, key=lambda x: x["percentage"], reverse=True)
        st.session_state.pdf_data = create_pdf_bytes(sorted_list, st.session_state.pass_marks)
        st.session_state.students = []
        save_students([])
        st.success(f"✅ PDF Ready! {st.session_state.pass_marks:.0f}% wale rule se bani hai. List clear!")
        st.balloons()

    if st.session_state.pdf_data:
        st.download_button(
            label="⬇️ Royal PDF Download Karo",
            data=st.session_state.pdf_data,
            file_name=f"Royal_Merit_List_{datetime.now().strftime('%d%m%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
else:
    if st.session_state.pdf_data:
        st.success("✅ PDF Ready hai! List clear ho chuki hai.")
        st.download_button(
            label="⬇️ Royal PDF Download Karo",
            data=st.session_state.pdf_data,
            file_name=f"Royal_Merit_List_{datetime.now().strftime('%d%m%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
        if st.button("🆕 Nayi List Banao"):
            st.session_state.pdf_data = None
            st.rerun()
    else:
        st.info("ℹ️ Koi student nahi hai. Sidebar se add karo.")