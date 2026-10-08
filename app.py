import streamlit as st
import pandas as pd
import json
import os
import hashlib
import time
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

st.set_page_config(page_title="M Saad Software - Maulana Azad", layout="wide")

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
    try:
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"expiry": (datetime.now() + timedelta(days=30)).isoformat()}

def save_license(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

license_data = load_license()
expiry_date = datetime.fromisoformat(license_data["expiry"])
is_locked = datetime.now() > expiry_date

if is_locked:
    st.error(f"🔒 Software Locked! Expiry: {expiry_date.strftime('%d-%m-%Y')}")
    st.markdown("### Contact M Saad - 7387246146 for Recharge")
    with st.expander("Admin Login (Only for M Saad)"):
        pwd = st.text_input("Admin Password", type="password")
        if pwd == ADMIN_PASSWORD:
            st.success("Welcome Boss!")
            days = st.number_input("Kitne din ka code?", 1, 1000, 30)
            if st.button("Generate Code"):
                code = f"MAZAD{days}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:6].upper()}"
                st.code(code)
            st.divider()
            direct = st.number_input("Direct Recharge Days", 1, 1000, 30, key="direct")
            if st.button("Recharge Now"):
                new_exp = datetime.now() + timedelta(days=direct)
                save_license({"expiry": new_exp.isoformat()})
                st.success(f"Recharged till {new_exp.strftime('%d-%m-%Y')}")
                time.sleep(1)
                st.rerun()
    ac = st.text_input("Activation Code")
    if st.button("Activate"):
        if ac.startswith("MAZAD"):
            try:
                d = int(ac.split("-")[0].replace("MAZAD",""))
                new_exp = datetime.now() + timedelta(days=d)
                save_license({"expiry": new_exp.isoformat()})
                st.success(f"Activated {d} days!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("Galat Code")
        else:
            st.error("Invalid Code")
    st.stop()

days_left = (expiry_date - datetime.now()).days
st.sidebar.info(f"⏰ Expiry: {expiry_date.strftime('%d-%m-%Y')} | {days_left} din baki")

with st.sidebar.expander("🔐 M Saad Code Generator"):
    p = st.text_input("Password", type="password", key="gen")
    if p == ADMIN_PASSWORD:
        gd = st.number_input("Days", 1, 1000, 30, key="gd")
        if st.button("Generate"):
            c = f"MAZAD{gd}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:6].upper()}"
            st.code(c)

st.markdown(f"<h2 style='text-align:center; color:#1e3a5f;'>{COLLEGE_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>{COLLEGE_LINE2}</p>", unsafe_allow_html=True)
st.divider()

uploaded = st.file_uploader("Excel File Upload Karo", type=["xlsx","xls"])

def generate_royal_pdf(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=80, bottomMargin=50, leftMargin=30, rightMargin=30)
    story = []

    headers = [str(c).upper() for c in df.columns.tolist()]
    table_data = [headers]
    for _, row in df.iterrows():
        vals = []
        for v in row:
            vals.append(str(v))
        table_data.append(vals)

    col_widths = [60, 220, 80, 60, 115]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#0e8a7a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.6, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, HexColor('#eaf6f3')]),
    ])
    table.setStyle(style)
    story.append(Spacer(1, 0.3*inch))
    story.append(table)

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(HexColor('#1e3a5f'))
        canvas.rect(0, 720, 595, 90, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawCentredString(297.5, 770, COLLEGE_NAME)
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(297.5, 745, COLLEGE_LINE2)
        canvas.setFillColor(HexColor('#666666'))
        canvas.setFont("Helvetica-Oblique", 7)
        canvas.drawString(120, 30, "Thank you! | Powered by M Saad Software - 7387246146")
        canvas.drawRightString(520, 20, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

if uploaded:
    df = pd.read_excel(uploaded)
    st.success(f"{len(df)} Students Loaded")
    st.dataframe(df, use_container_width=True)
    if st.button("📄 Generate Royal PDF (2nd Photo Jaisi)", type="primary"):
        fname = f"Maulana_Azad_Merit_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
        generate_royal_pdf(df, fname)
        with open(fname, "rb") as f:
            st.download_button("📥 PDF Download Karo", f, file_name=fname, mime="application/pdf")
        st.success("Ho gaya bhai! Bilkul Royal PDF ready!")