import streamlit as st
import mysql.connector

# Function to connect to MySQL database
def get_connection():
    return mysql.connector.connect(
        host="82.180.143.66", 
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )

# Function to insert patient data
def insert_patient(data):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO E_casepatient 
        (Name, RFIDNO, Age, Gender, BloodGroup, DateofBirth, ContactNo, EmailID, Address, DoctorAssigned)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, data)
    conn.commit()
    cursor.close()
    conn.close()

# Streamlit form
st.title("Patient Registration Form")

with st.form("patient_form"):
    name = st.text_input("Full Name")
    rfid = st.text_input("RFID No")
    age = st.text_input("Age")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    blood_group = st.text_input("Blood Group")
    dob = st.date_input("Date of Birth")
    contact = st.text_input("Contact Number")
    email = st.text_input("Email ID")
    address = st.text_area("Address")
    doctor = st.text_input("Doctor Assigned")

    submitted = st.form_submit_button("Register Patient")

    if submitted:
        try:
            insert_patient((name, rfid, age, gender, blood_group, dob.strftime('%Y-%m-%d'),
                            contact, email, address, doctor))
            st.success("Patient registered successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

