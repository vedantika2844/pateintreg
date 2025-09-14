import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# ----------------- DB Connection -----------------
def get_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )

# ----------------- Insert Patient -----------------
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

# ----------------- Get All Patients -----------------
def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM E_casepatient ORDER BY ID DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# ----------------- Get Medical History -----------------
def get_all_medical_history():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM medical_histroy ORDER BY ID DESC")  # ✅ table name fixed
        rows = cursor.fetchall()
        if not rows or cursor.description is None:
            return []
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        st.error(f"❌ Error fetching medical history: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ----------------- Get Current Appointments -----------------
elif menu == "Current Appointments":
    st.subheader("📅 Current Appointments")
    try:
        appointments = get_current_appointments()
        if appointments:
            df = pd.DataFrame(appointments)

            # Only keep necessary columns
            display_df = df[['RFID_No', 'Date_Time', 'Status']].copy()

            # Convert to HTML to allow links to be clickable
            html_table = display_df.to_html(escape=False, index=False)

            st.markdown("### Appointments Table")
            st.write(html_table, unsafe_allow_html=True)

        else:
            st.info("No current appointments found.")
    except Exception as e:
        st.error(f"❌ Error fetching appointments: {e}")


# ----------------- Streamlit UI -----------------

st.set_page_config(page_title="Patient Registration", layout="wide")
st.title("🧾 Patient Registration System")

# ✅ Check for query param to display medical history directly
rfid_filter = st.query_params.get("rfid_filter", [None])[0]

if rfid_filter:
    st.subheader(f"📖 Medical History for RFID: {rfid_filter}")
    try:
        data = get_all_medical_history()
        filtered_data = [record for record in data if record.get('RFID_No') == rfid_filter or record.get('RFIDNO') == rfid_filter]

        if filtered_data:
            df = pd.DataFrame(filtered_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No medical history records found for this RFID.")
    except Exception as e:
        st.error(f"❌ Error fetching medical history: {e}")

    st.markdown("[🔙 Back to Main Page](./)", unsafe_allow_html=True)
    st.stop()

# --------------- Menu Navigation ----------------

menu = st.sidebar.radio("Menu", ["Register Patient", "View All Patients", "View Medical History", "Current Appointments"])

# ---------------- Register Patient ----------------
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

                insert_patient((
                    name, rfid, age, gender, blood_group, dob_str,
                    contact, email, address, doctor
                ))

                st.success("✅ Patient registered successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ---------------- View All Patients ----------------
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

# ---------------- View Medical History ----------------
elif menu == "View Medical History":
    st.subheader("📖 Medical History Records")
    try:
        rfid_input = st.text_input("Enter RFID No to filter (optional)")
        data = get_all_medical_history()

        if rfid_input:
            data = [r for r in data if r.get('RFID_No') == rfid_input or r.get('RFIDNO') == rfid_input]

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No medical history records found.")
    except Exception as e:
        st.error(f"❌ Error fetching medical history: {e}")

# ---------------- Current Appointments ----------------
elif menu == "Current Appointments":
    st.subheader("📅 Current Appointments")
    try:
        appointments = get_current_appointments()
        if appointments:
            df = pd.DataFrame(appointments)

            # Use markdown to display with HTML links
            for _, row in df.iterrows():
                rfid = row.get('RFID_No', 'N/A')
                date_time = row.get('Date_Time', 'N/A')
                status = row.get('Status', '')

                st.markdown(f"""
                **RFID:** {rfid}  
                **Date/Time:** {date_time}  
                **Status:** {status}  
                ---
                """, unsafe_allow_html=True)
        else:
            st.info("No current appointments found.")
    except Exception as e:
        st.error(f"❌ Error fetching appointments: {e}")
