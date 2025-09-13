import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

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
    
    def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM E_casepatient ORDER BY ID DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Function to fetch all registered patients
def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM E_casepatient ORDER BY ID DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
    
    def get_all_medical_history():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM `medical_histroy` ORDER BY `ID` DESC")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cursor.close()
        conn.close()

# Streamlit App
st.title("🧾 Patient Registration System")

menu = st.sidebar.radio("Menu", ["Register Patient", "View All Patients"])

if menu == "Register Patient":
    with st.form("patient_form"):
        st.subheader("Register New Patient")

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
                # Convert and validate age
                try:
                    age = int(age)
                except ValueError:
                    st.error("❌ Age must be a number.")
                    st.stop()

                # Ensure dob is in string format
                if isinstance(dob, str):
                    dob_str = dob  # unlikely, but safe fallback
                else:
                    dob_str = dob.strftime('%Y-%m-%d')

                # Insert into DB
                insert_patient((
                    name, rfid, age, gender, blood_group, dob_str,
                    contact, email, address, doctor
                ))

                st.success("✅ Patient registered successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

elif menu == "View All Patients":
    st.subheader("📋 All Registered Patients")

    try:
        data = get_all_patients()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No patients registered yet.")
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        elif menu == "View Medical History":
    st.subheader("📖 Medical History Records")

    try:
        # Optional: Filter by RFIDNo
        rfid_filter = st.text_input("Enter RFID No to filter (optional)")

        data = get_all_medical_history()
        if rfid_filter:
             data = [record for record in data if record['RFIDNo'] == rfid_filter]
  if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No medical history records found.")
    except Exception as e:
 st.error(f"❌ Error fetching medical history: {e}")
        
