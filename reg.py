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

# -------------------- Delete Appointment by RFID --------------------
def delete_appointment_by_rfid(rfid):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM E_Case WHERE RFID_No = %s", (rfid,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete appointment with RFID {rfid}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="Patient System", layout="wide")
st.title("🧾 Patient Registration System")

# Sidebar menu
menu = st.sidebar.radio("Menu", ["Register Patient", "View All Patients", "View Medical History", "Current Appointments"])

# Other menu codes (Register, View Patients, Medical History) remain the same...
# For brevity, skipping unchanged parts...

# -------------------- Current Appointments --------------------
if menu == "Current Appointments":
    st.subheader("📅 Current Appointments")

    appointments = get_current_appointments()

    if not appointments:
        st.info("No current appointments found.")
    else:
        # Create dataframe for display
        df = pd.DataFrame(appointments)

        # Check necessary columns exist
        if {'RFID_No', 'Date_Time', 'Status'}.issubset(df.columns):
            # Prepare status display (Active / Inactive)
            def status_label(status):
                if status == 1:
                    return "🟢 Active"
                else:
                    return "🔴 Inactive"

            df_display = df[['RFID_No', 'Date_Time', 'Status']].copy()
            df_display['Status'] = df_display['Status'].apply(status_label)

            # Display table with buttons
            for idx, row in df_display.iterrows():
                cols = st.columns([3, 3, 2, 2])
                cols[0].write(f"**RFID:** {row['RFID_No']}")
                cols[1].write(f"**Date & Time:** {row['Date_Time']}")
                cols[2].write(f"**Status:** {row['Status']}")

                # Update button in status column if status == 1
                original_status = df.loc[idx, 'Status']
                if original_status == 1:
                    if cols[3].button(f"Update", key=f"update_{row['RFID_No']}"):
                        # Delete row from E_Case where RFID_No matches
                        deleted = delete_appointment_by_rfid(row['RFID_No'])
                        if deleted:
                            st.success(f"✅ Appointment with RFID {row['RFID_No']} deleted.")
                            st.experimental_rerun()
                        else:
                            st.error(f"❌ Failed to delete appointment with RFID {row['RFID_No']}.")
                else:
                    cols[3].write("")  # Empty for inactive status

        else:
            st.warning("Required columns missing in appointments data.")
            st.dataframe(df)
