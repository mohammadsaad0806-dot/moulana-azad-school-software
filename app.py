import streamlit as st
from fpdf import FPDF
from datetime import datetime

# ==========================================
# SCHOOL DETAILS - tu yaha se change kar sakta hai
# ==========================================
SCHOOL_NAME = "MAULANA AZAD URDU HIGH SCHOOL & JUNIOR COLLEGE"
SCHOOL_ADDRESS = "DHAD"
SCHOOL_PHONE = "9021222111"
SOFTWARE_NAME = "M Saad Software"
SOFTWARE_PHONE = "7387246146"

st.set_page_config(page_title="M Saad School Software", layout="wide")
st.title("🏫 M Saad School Software")
st.caption(f"{SCHOOL_NAME} - Royal List Generator")

if "students" not in st.session_state:
    st.session_state.students = []

# --- Sidebar input ---
with st.sidebar:
    st.header("Student Add Karo")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Student ka naam")
        gender = st.selectbox("Gender", ["FEMALE", "MALE"])
        sclass = st.selectbox("Class", list(range(1,13)), index=11)
        perc = st.number_input("Percentage", 0.0, 100.0, 60.0, step=0.1)
        submitted = st.form_submit_button("➕ Add Student")
        if submitted and name.strip()!= "":
            st.session_state.students.append({
                "name": name.strip(),
                "gender": gender,
                "class": str(sclass),
                "percentage": perc
            })
            st.success(f"{name} added!")
        elif submitted:
            st.error("Naam blank hai!")

    if st.button("🗑️ Sab Clear Karo"):
        st.session_state.students = []
        st.rerun()

# --- Main Table View ---
if st.session_state.students:
    st.subheader(f"Total Students: {len(st.session_state.students)}")
    st.dataframe(st.session_state.students, use_container_width=True)
else:
    st.info("Abhi koi student add nahi hua. Sidebar se add karna start karo.")

# --- PDF CLASS - Tera hi design ---
class StudentPDF(FPDF):
    def header(self):
        self.set_fill_color(25, 55, 95)
        self.rect(0, 0, 297, 34, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 15)
        self.set_xy(8, 7)
        self.cell(281, 8, SCHOOL_NAME, align="C")
        self.set_font("Helvetica", "", 10)
        self.set_xy(8, 18)
        self.cell(281, 6, f"{SCHOOL_ADDRESS} | Phone: {SCHOOL_PHONE}", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(39)

if st.button("📄 Royal PDF Banao aur Link Se Download Karo", type="primary", disabled=len(st.session_state.students)==0):
    students = st.session_state.students
    students_per_page = 10
    total_students = len(students)
    total_pages = (total_students + students_per_page - 1) // students_per_page

    pdf = StudentPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    for page_start in range(0, total_students, students_per_page):
        pdf.add_page()
        page_students = students[page_start:page_start+students_per_page]

        col_widths = [20, 115, 40, 30, 75]
        headers = ["SR. NO.", "NAME OF STUDENT", "GENDER", "CLASS", "PERCENTAGE"]

        pdf.set_fill_color(0, 150, 136)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 11, header, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Helvetica", "", 10)
        for index, student in enumerate(page_students):
            global_index = page_start + index + 1
            if index % 2 == 0:
                pdf.set_fill_color(240, 248, 250)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(30, 30, 30)

            pdf.cell(col_widths[0], 12, str(global_index), border=1, align="C", fill=True)
            pdf.cell(col_widths[1], 12, student["name"][:45], border=1, align="L", fill=True)
            pdf.cell(col_widths[2], 12, student["gender"], border=1, align="C", fill=True)
            pdf.cell(col_widths[3], 12, student["class"], border=1, align="C", fill=True)

            percentage_text = f"{student['percentage']:.2f}%"
            if student["percentage"] >= 56:
                pdf.set_text_color(0, 110, 80)
                pdf.set_font("Helvetica", "B", 10)
            pdf.cell(col_widths[4], 12, percentage_text, border=1, align="C", fill=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.ln()

        # Footer
        pdf.set_y(194)
        pdf.set_text_color(90, 90, 90)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(281, 6, f"Thank you! | Powered by {SOFTWARE_NAME} - {SOFTWARE_PHONE}", align="C")
        pdf.set_y(201)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(130, 130, 130)
        current_page = (page_start // students_per_page) + 1
        pdf.cell(281, 4, f"Page {current_page} of {total_pages}", align="R")

    file_name = f"Student_Percentage_List_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(file_name)
    with open(file_name, "rb") as f:
        st.success("✅ PDF Ban Gayi!")
        st.download_button("📥 Download PDF", f, file_name=file_name, mime="application/pdf")
