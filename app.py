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
from reportlab.lib.colors import HexColor

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
    st.error(f"🔒 Locked! {expiry_date.strftime('%d-%m-%Y')}")
    st.stop()

def generate_royal_pdf(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=90, bottomMargin=50, leftMargin=30, rightMargin=30)
    story = []

    headers = [str(c).strip().upper() for c in df.columns.tolist()]
    table_data = [headers]
    for _, row in df.iterrows():
        table_data.append([str(v) for v in row.tolist()])

    col_widths = [55, 210, 75, 55, 110]
    if len(headers)!= 5:
        col_widths = None

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
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
    ]))
    story.append(Spacer(1, 20))
    story.append(table)

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(HexColor('#1e3a5f'))
        canvas.rect(0, 750, 595, 92, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawCentredString(297.5, 800, COLLEGE_NAME)
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(297.5, 775, COLLEGE_LINE2)
        canvas.setFillColor(HexColor('#666666'))
        canvas.setFont("Helvetica-Oblique", 7)
        canvas.drawCentredString(297.5, 30, "Thank you! | Powered by M Saad Software - 7387246146")
        canvas.drawRightString(560, 15, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

st.markdown(f"<h2 style='text-align:center; color:#1e3a5f;'>{COLLEGE_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>{COLLEGE_LINE2}</p>", unsafe_allow_html=True)
st.divider()

uploaded = st.file_uploader("Excel File Upload Karo", type=["xlsx", "xls"])
if uploaded:
    df = pd.read_excel(uploaded)
    st.dataframe(df, use_container_width=True)
    if st.button("📄 Generate Royal PDF", type="primary"):
        fname = f"Merit_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"
        generate_royal_pdf(df, fname)
        with open(fname, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=fname, mime="application/pdf")