import streamlit as st
import pandas as pd
from recognize import recognize_faces
import tempfile
import os
from datetime import datetime
import sqlite3

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Attendance", layout="wide")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📘 AI Attendance System")
st.sidebar.write("Smart Face Recognition")

# =========================
# LOGIN
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Teacher Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    name TEXT,
    enroll TEXT,
    subject TEXT,
    date TEXT,
    time TEXT,
    present INTEGER
)
""")
conn.commit()

# =========================
# SESSION
# =========================
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# =========================
# TEACHER FORM
# =========================
if not st.session_state.form_submitted:

    st.title("🎓 AI Attendance System")
    st.header("👨‍🏫 Enter Teacher Details")

    with st.form("teacher_form"):
        t_name = st.text_input("Teacher Name")
        t_id = st.text_input("Teacher ID")
        subject = st.text_input("Subject")
        period = st.text_input("Period")

        submit = st.form_submit_button("Proceed")

        if submit:
            st.session_state.form_submitted = True
            st.session_state.teacher = {
                "name": t_name,
                "id": t_id,
                "subject": subject,
                "period": period
            }
            st.rerun()

# =========================
# MAIN APP
# =========================
if st.session_state.form_submitted:

    teacher = st.session_state.teacher

    st.success(
        f"👨‍🏫 {teacher['name']} | 📘 {teacher['subject']} | ⏱ Period: {teacher['period']}"
    )

    if st.button("🔄 Reset"):
        st.session_state.form_submitted = False
        st.rerun()

    st.header("📤 Upload Classroom Images")

    uploaded_files = st.file_uploader(
        "Upload images",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )

    st.subheader("📸 OR Use Camera")
    camera_img = st.camera_input("Capture Image")

    all_results = []

    # PROCESS UPLOAD
    if uploaded_files:
        for file in uploaded_files:
            temp_dir = tempfile.mkdtemp()
            path = os.path.join(temp_dir, file.name)

            with open(path, "wb") as f:
                f.write(file.read())

            st.image(path, caption=file.name, use_column_width=True)

            results = recognize_faces(path)
            if isinstance(results, list):
                all_results.extend(results)

    # PROCESS CAMERA
    if camera_img:
        with open("temp.jpg", "wb") as f:
            f.write(camera_img.getbuffer())

        st.image("temp.jpg", caption="Captured Image", use_column_width=True)

        results = recognize_faces("temp.jpg")
        if isinstance(results, list):
            all_results.extend(results)

    # REMOVE DUPLICATES
    unique_students = {}
    for r in all_results:
        unique_students[r["enroll"]] = r

    final_results = list(unique_students.values())

    if len(final_results) == 0:
        st.warning("No students detected ❌")

    else:
        st.success(f"✅ {len(final_results)} students detected")

        st.subheader("📋 Mark Attendance")

        attendance_data = []

        for i, r in enumerate(final_results):

            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])

            with col1:
                if r.get("face") is not None:
                    st.image(r["face"], width=100)

            with col2:
                st.write(f"👤 **{r.get('name', 'Unknown')}**")

                conf = r.get("confidence", 0)

                if conf > 70:
                    st.success(f"Confidence: {conf:.2f}%")
                elif conf > 50:
                    st.warning(f"Confidence: {conf:.2f}%")
                else:
                    st.error(f"Confidence: {conf:.2f}%")

            with col3:
                st.write(f"🎫 **{r.get('enroll', 'N/A')}**")

            with col4:
                present = st.checkbox("✔", key=i, value=True)

            attendance_data.append({
                "name": str(r.get("name", "")),
                "enroll": str(r.get("enroll", "")),
                "confidence": float(r.get("confidence", 0)),
                "present": present
            })

        # ADD ABSENT STUDENTS
        all_students = pd.read_csv("names_enroll_branch.csv")
        detected_enrolls = [r["enroll"] for r in final_results]

        for _, row in all_students.iterrows():
            if str(row["enroll_no"]) not in detected_enrolls:
                attendance_data.append({
                    "name": row["name"],
                    "enroll": row["enroll_no"],
                    "confidence": 0,
                    "present": False
                })

        # SAVE
        if st.button("💾 Save Attendance"):

            df = pd.DataFrame(attendance_data)

            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")

            df["date"] = date
            df["time"] = time

            file_name = f"attendance_{date}_{teacher['subject']}.csv"
            df.to_csv(file_name, index=False)

            for _, row in df.iterrows():
                cursor.execute("""
                INSERT INTO attendance VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row["name"],
                    row["enroll"],
                    teacher["subject"],
                    row["date"],
                    row["time"],
                    int(row["present"])
                ))

            conn.commit()

            st.success("🎉 Attendance Saved Successfully!")

            st.download_button(
                "⬇ Download Attendance",
                df.to_csv(index=False),
                file_name
            )

            # DASHBOARD
            total = len(df)
            present = df["present"].sum()
            absent = total - present

            col1, col2, col3 = st.columns(3)
            col1.metric("Total", total)
            col2.metric("Present", present)
            col3.metric("Absent", absent)

            # ACCURACY
            correct = len(df[df["confidence"] > 50])
            accuracy = (correct / total) * 100 if total > 0 else 0
            st.info(f"🎯 System Accuracy: {accuracy:.2f}%")

            st.dataframe(df)
