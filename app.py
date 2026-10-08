import streamlit as st
import pandas as pd
import json
import os
import hashlib
import time
from datetime import datetime, timedelta
from fpdf import FPDF

st.set_page_config(page_title="M Saad Software", layout="wide")

ADMIN_PASSWORD = "Saad@786"
LICENSE_FILE = "license.json"
COLLEGE_NAME = "MAULANA AZAD URDU HIGH SCHOOL & JUNIOR COLLEGE"
COLLEGE_LINE2 = "DHAD | Phone: 9021222111"

def load_license():
    if not os.path.exists(LICENSE_FILE):
        data = {"expiry": (datetime.now() + timedelta(days=30)).isoformat()}
        with open(LICENSE_FILE, "w") as f:
            json.dump(data, f)
        return data
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_license(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

license_data = load_license()
expiry_date = datetime.fromisoformat(license_data["expiry"])

if datetime.now() > expiry_date:
    st.error(f"🔒 Locked! Expiry: {expiry_date.strftime('%d-%m-%Y')}")
    with st.expander("Admin Login"):
        pwd = st.text_input("Password", type="password")
        if pwd == ADMIN_PASSWORD:
            days = st.number_input("Days", 1, 1000, 30)
            if st.button("Generate Code"):
                code = f"MAZAD{days}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:6].upper()}"
                st.code(code)
            if st.button("Direct Recharge"):
                save_license({"expiry": (datetime.now() + timedelta(days=30)).isoformat()})
                st.rerun()
    code_in = st.text_input("Activation Code")
    if st.button("Activate"):
        if code_in.startswith("MAZAD"):
            try:
                d = int(code_in.split("-")[0].replace("MAZAD",""))
                save_license({"expiry": (datetime.now() + timedelta(days=d)).isoformat()})
                st.rerun()
            except:
                st.error("Invalid Code")
    st.stop()

def generate_royal_pdf(df, filename):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- Top Blue Header ---
    pdf.set_fill_color(30, 58, 95) # #1e3a5f
    pdf.rect(0, 0, 210, 32, 'F')
    pdf.set_y(8)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, COLLEGE_NAME, align='C', ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, COLLEGE_LINE2, align='C', ln=True)

    pdf.ln(20)

    # --- Table Header ---
    col_widths = [15, 75, 25, 20, 35]
    headers = [str(c).upper() for c in df.columns.tolist()]
    # If 5 cols not matching, adjust
    if len(headers)!= 5:
        col_widths = [190 / len(headers)] * len(headers)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(14, 138, 122) # #0e8a7a
    pdf.set_text_color(255,255,255)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, h, border=1, align='C', fill=True)
    pdf.ln()

    # --- Table Rows ---
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0,0,0)
    fill = False
    for _, row in df.iterrows():
        if fill:
            pdf.set_fill_color(234, 246, 243) # #eaf6f3
        else:
            pdf.set_fill_color(255,255,255)

        max_h = 10
        # Row data
        vals = [str(v) for v in row.tolist()]
        for i, val in enumerate(vals):
            align = 'C'
            if i == 1:
                align = 'L'
            pdf.cell(col_widths[i], 10, val, border=1, align=align, fill=True)
        pdf.ln()
        fill = not fill

    # --- Footer ---
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100,100,100)
    pdf.cell(0, 10, "Thank you! | Powered by M Saad Software - 7387246146", align='C')

    pdf.output(filename)

# --- UI ---
st.markdown(f"<h2 style='text-align:center; color:#1e3a5f;'>{COLLEGE_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>{COLLEGE_LINE2}</p>", unsafe_allow_html=True)
st.divider()

uploaded = st.file_uploader("Excel File Upload Karo", type=["xlsx", "xls"])

if uploaded:
    df = pd.read_excel(uploaded)
    st.success(f"{len(df)} Students Loaded")
    st.dataframe(df, use_container_width=True)
    if st.button("📄 Generate Royal PDF", type="primary"):
        fname = f"Merit_List_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"
        generate_royal_pdf(df, fname)
        with open(fname, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=fname, mime="application/pdf")
        st.success("Ho gaya! Bilkul 2nd photo jaisi Royal PDF!")