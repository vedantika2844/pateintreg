import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# -------------------- DB Connection -------------------- 
def get_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )

# -------------------- Insert Patient --------------------
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

# -------------------- Fetch All Patients --------------------
def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM E_casepatient ORDER BY ID DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# -------------------- Fetch Medical History --------------------
def get_medical_history_by_rfid(rfidno="41E2014B"):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT * 
            FROM medical__histroy
            WHERE RFIDNo = %s
            ORDER BY ID DESC
            """,
            (rfidno,)
        )
        rows = cursor.fetchall()
        st.write(f"Filtering by RFIDNo: {rfidno}")
        return rows if rows else []

    except Exception as e:
        st.error(f"❌ Error fetching medical history for RFID {rfidno}: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# -------------------- Fetch Appointments --------------------
def get_current_appointments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM E_Case ORDER BY Date_Time DESC")
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        st.error(f"❌ Failed to fetch appointments: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# -------------------- Delete Appointment By RFID --------------------
def delete_appointment_by_rfid(rfid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM E_Case WHERE RFID_No = %s", (rfid,))
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        return affected_rows > 0
    except Exception as e:
        st.error(f"❌ Error deleting appointment with RFID {rfid}: {e}")
        return False

# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="Patient System", layout="wide")
st.title("🧾 Patient Registration System")

# ✅ Check for RFID in query params to directly show medical history
rfid_filter = st.query_params.get("rfid_filter", [None])[0]

if rfid_filter:
    st.subheader(f"📖 Medical History for RFID: {rfid_filter}")
    try:
        data = get_medical_history_by_rfid(rfid_filter)
        filtered_data = [record for record in data if record.get('RFIDNo') == rfid_filter]

        if filtered_data:
            df = pd.DataFrame(filtered_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No medical history records found for this RFID.")
    except Exception as e:
        st.error(f"❌ Error fetching medical history: {e}")

    st.markdown("[🔙 Back to Main Page](./)", unsafe_allow_html=True)
    st.stop()

# -------------------- Sidebar Menu --------------------
menu = st.sidebar.radio("Menu", ["Register Patient", "View All Patients", "View Medical History", "Current Appointments"])

# -------------------- Register Patient --------------------
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
                try:
                    age = int(age)
                except ValueError:
                    st.error("❌ Age must be a number.")
                    st.stop()

                dob_str = dob.strftime('%Y-%m-%d')

                insert_patient((name, rfid, age, gender, blood_group, dob_str,
                                contact, email, address, doctor))
                st.success("✅ Patient registered successfully!")

            except Exception as e:
                st.error(f"❌ Error: {e}")

# -------------------- View All Patients --------------------
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
        st.error(f"❌ Error fetching patients: {e}")

# -------------------- View Medical History -------------------
elif menu == "View Medical History":
    st.subheader("📖 Medical History Records")

    try:
        appointments = get_current_appointments()
        rfid_list = [row['RFID_No'] for row in appointments if row.get('RFID_No')]

        if rfid_list:
            selected_rfid = st.selectbox("Select RFID to view history", rfid_list)

            if selected_rfid:
                data = get_medical_history_by_rfid(selected_rfid)

                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning(f"No medical history found for RFID {selected_rfid}")
        else:
            st.info("No RFID numbers found in current appointments.")

    except Exception as e:
        st.error(f"❌ Error fetching medical history: {e}")

# -------------------- Current Appointments -------------------- 
elif menu == "Current Appointments":
    st.subheader("📅 Current Appointments")
    try:
        appointments = get_current_appointments()

        if appointments:
            df = pd.DataFrame(appointments)

            if {'RFID_No', 'Date_Time', 'Status'}.issubset(df.columns):
                # Show table header
                st.markdown("### Appointments Table")

                # Iterate rows to display with update buttons conditionally
                for i, row in df.iterrows():
                    cols = st.columns([3, 3, 2, 1])
                    cols[0].write(f"**RFID:** {row['RFID_No']}")
                    cols[1].write(f"**Date & Time:** {row['Date_Time']}")

                    # Status display with colored dot and text
                    try:
                        status_value = int(row['Status'])
                    except Exception:
                        status_value = 0

                    if status_value == 1:
                        status_str = "🟢 Active"
                    else:
                        status_str = "🔴 Inactive"

                    cols[2].write(f"**Status:** {status_str}")

                    # Show update button only if status == 1
                    if status_value == 1:
                        if cols[3].button("Update", key=f"update_{row['RFID_No']}"):
                            deleted = delete_appointment_by_rfid(row['RFID_No'])
                            if deleted:
                                st.success(f"✅ Appointment with RFID {row['RFID_No']} deleted.")
                                st.experimental_rerun()
                            else:
                                st.error(f"❌ Failed to delete appointment with RFID {row['RFID_No']}.")
                    else:
                        cols[3].write("")  # Empty cell when no button

            else:
                st.warning("Expected columns not found in appointment data.")
                st.dataframe(df)

        else:
            st.info("No current appointments found.")

    except Exception as e:
        st.error(f"❌ Error fetching appointments: {e}")
