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

# Function to fetch all registered patients
def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM E_casepatient ORDER BY ID DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Function to fetch medical history records

    def get_all_medical_history():
      conn = get_connection()
      cursor = conn.cursor()
    try:
        # ✅ Make sure the table name is spelled correctly
        cursor.execute("SELECT * FROM medical_history ORDER BY ID DESC")
        rows = cursor.fetchall()

        # ✅ Prevents crash if cursor.description is None
        if not rows or cursor.description is None:
            return []
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        
# Function to fetch current appointment records

  def get_current_appointments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM appointments
            WHERE appointment_datetime >= NOW()
            ORDER BY appointment_datetime ASC
        """)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        st.error(f"❌ Failed to fetch current appointments: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Streamlit App
st.title("🧾 Patient Registration System")

menu = st.sidebar.radio("Menu", ["Register Patient", "View All Patients", "View Medical History"])

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
                # Validate age
                try:
                    age = int(age)
                    ValueError:
                    st.error("❌ Age must be a number.")
                    st.stop()

                # Convert DOB
                dob_str = dob.strftime('%Y-%m-%d')

                # Insert into DB
                insert_patient((
                    name, rfid, age, gender, blood_group, dob_str,
                    contact, email, address, doctor
                ))

                st.success("✅ Patient registered successfully!")
                 Exception as e:
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
            Exception as e:
        st.error(f"❌ Error fetching data: {e}")

elif menu == "View Medical History":
    st.subheader("📖 Medical History Records")

    try:
        rfid_filter = st.text_input("Enter RFID No to filter (optional)")
        data = get_all_medical_history()

        if rfid_filter:
            data = [record for record in data if record['RFIDNo'] == rfid_filter]

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No medical history records found.")
            Exception as e:
        st.error(f"❌ Error fetching medical history: {e}")
     
elif menu == "Current Appointments":
    st.subheader("📅 Current Appointments")

    try:
        appointments = get_current_appointments()
        if appointments:
            df = pd.DataFrame(appointments)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No current appointments found.")
            Exception as e:
        st.error(f"❌ Error fetching appointments: {e}")
