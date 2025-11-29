# ggi_student_auth_app.py
import streamlit as st
import json
import os
import hashlib
from datetime import datetime

# ---------- CONFIG ----------
APP_TITLE = "GGI STUDENT MANAGEMENT (Auth)"
DATA_FILE = "students_auth.json"

# === Personal / College info you asked to show ===
COLLEGE_NAME = "Global Group of Institutes, Amritsar"
AUTHOR_NAME = "Shubhdeep Singh"
AUTHOR_ROLL = "2430331"
FRIEND_NAME = " vishaldeep singh"       # <-- change this to your friend's name
FRIEND_ROLL = "2430349"    # <-- change this to your friend's roll number

# Set admin credentials (change these if you want)
ADMIN_USERNAME = "admin"
ADMIN_PLAIN_PASSWORD = "ggi1234"  # change this in code later if needed

# store hashed admin password (do not change variable name)
ADMIN_PW_HASH = hashlib.sha256(ADMIN_PLAIN_PASSWORD.encode()).hexdigest()

# ---------- Helpers ----------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(pw: str):
    return hashlib.sha256(pw.encode()).hexdigest()

def ensure_default_students(students_list):
    """
    Ensure author and friend records exist in students_list.
    Adds them if missing (no duplicates).
    """
    changed = False
    # normalize rolls as strings
    a_roll = str(AUTHOR_ROLL)
    f_roll = str(FRIEND_ROLL)

    # Check author
    if not any(s.get("roll") == a_roll for s in students_list):
        students_list.append({
            "name": AUTHOR_NAME,
            "roll": a_roll,
            "course": "B.Tech CSE",
            "year": "1st",
            "marks": 0,
            "phone": "",
            "email": "",
            "created_at": datetime.now().isoformat()
        })
        changed = True

    # Check friend
    if FRIEND_ROLL and not any(s.get("roll") == f_roll for s in students_list):
        students_list.append({
            "name": FRIEND_NAME,
            "roll": f_roll,
            "course": "B.Tech CSE",
            "year": "1st",
            "marks": 0,
            "phone": "",
            "email": "",
            "created_at": datetime.now().isoformat()
        })
        changed = True

    if changed:
        save_data(students_list)

# ---------- Streamlit Page ----------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.markdown(f"### {APP_TITLE}")
st.markdown(f"**{COLLEGE_NAME}**")
st.markdown(f"**Author:** {AUTHOR_NAME} (Roll: {AUTHOR_ROLL})  •  **Team Member:** {FRIEND_NAME} (Roll: {FRIEND_ROLL})")
st.write("---")

# session state for login
if "role" not in st.session_state:
    st.session_state.role = None
if "user" not in st.session_state:
    st.session_state.user = None

students = load_data()
ensure_default_students(students)  # make sure author & friend records exist

# ----- Login layout -----
col1, col2 = st.columns([2,1])
with col1:
    st.markdown("### Login Panel")
with col2:
    if st.session_state.role:
        if st.button("Logout"):
            st.session_state.role = None
            st.session_state.user = None
            st.experimental_rerun()

login_type = st.selectbox("Login as", ["Select","Admin","Student"])

if login_type == "Admin":
    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PW_HASH:
            st.success("Admin login successful ✅")
            st.session_state.role = "admin"
            st.session_state.user = username
            st.experimental_rerun()
        else:
            st.error("Invalid admin credentials ❌")

elif login_type == "Student":
    st.info("Students login with their Roll Number (no password).")
    roll = st.text_input("Enter Roll Number")
    if st.button("Login as Student"):
        found = [s for s in students if s.get("roll") == str(roll)]
        if found:
            st.success("Student login successful ✅")
            st.session_state.role = "student"
            st.session_state.user = str(roll)
            st.experimental_rerun()
        else:
            st.error("Roll number not found. Ask admin to add your record.")

# ---------- Admin Dashboard ----------
if st.session_state.role == "admin":
    st.markdown("---")
    st.subheader("🔧 Admin Panel")
    admin_menu = st.selectbox("Choose action", ["Add Student","View/Edit Students","Search Student","Delete Student"])
    if admin_menu == "Add Student":
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            roll = st.text_input("Roll Number")
            course = st.text_input("Course")
            year = st.selectbox("Year", ["1st","2nd","3rd","4th"])
            marks = st.number_input("Marks", min_value=0, max_value=100, value=0)
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Add Student")
        if submitted:
            if not name or not roll:
                st.error("Name and Roll are required.")
            elif any(s["roll"] == str(roll) for s in students):
                st.error("A student with this roll already exists.")
            else:
                students.append({
                    "name": name,
                    "roll": str(roll),
                    "course": course,
                    "year": year,
                    "marks": int(marks),
                    "phone": phone,
                    "email": email,
                    "created_at": datetime.now().isoformat()
                })
                save_data(students)
                st.success("Student added successfully ✅")

    elif admin_menu == "View/Edit Students":
        st.write("All student records:")
        if students:
            # show table
            st.table([{k: s.get(k,"") for k in ("roll","name","course","year","marks","phone","email")} for s in students])
            st.markdown("### Edit a student record")
            edit_roll = st.text_input("Enter Roll No to edit")
            if st.button("Load for Edit"):
                rec = next((s for s in students if s["roll"] == str(edit_roll)), None)
                if rec:
                    st.session_state["edit_rec"] = rec
                else:
                    st.error("No record found.")
            if "edit_rec" in st.session_state:
                rec = st.session_state["edit_rec"]
                with st.form("edit_form"):
                    rec["name"] = st.text_input("Full Name", value=rec.get("name",""))
                    rec["course"] = st.text_input("Course", value=rec.get("course",""))
                    rec["year"] = st.selectbox("Year", ["1st","2nd","3rd","4th"], index=["1st","2nd","3rd","4th"].index(rec.get("year","1st")))
                    rec["marks"] = st.number_input("Marks", min_value=0, max_value=100, value=int(rec.get("marks",0)))
                    rec["phone"] = st.text_input("Phone", value=rec.get("phone",""))
                    rec["email"] = st.text_input("Email", value=rec.get("email",""))
                    save_btn = st.form_submit_button("Save Changes")
                if save_btn:
                    # update the students list
                    for i,s in enumerate(students):
                        if s["roll"] == rec["roll"]:
                            students[i] = rec
                            save_data(students)
                            st.success("Record updated ✅")
                            del st.session_state["edit_rec"]
                            break
                st.button("Clear Edit", on_click=lambda: st.session_state.pop("edit_rec", None))
        else:
            st.info("No students yet. Add from Add Student.")

    elif admin_menu == "Search Student":
        q = st.text_input("Enter Roll No to search")
        if st.button("Search"):
            result = [s for s in students if s["roll"] == str(q)]
            if result:
                st.json(result[0])
            else:
                st.error("No record found.")

    elif admin_menu == "Delete Student":
        droll = st.text_input("Enter Roll No to delete")
        if st.button("Delete"):
            before = len(students)
            students = [s for s in students if s["roll"] != str(droll)]
            if len(students) < before:
                save_data(students)
                st.success("Deleted successfully ✅")
            else:
                st.error("No such roll number.")

    st.markdown("---")
    st.caption(f"Logged in as: Admin ({st.session_state.user})")

# ---------- Student Dashboard ----------
elif st.session_state.role == "student":
    st.markdown("---")
    st.subheader("👨‍🎓 Student Panel (View Only)")
    roll = st.session_state.user
    rec = next((s for s in students if s["roll"] == str(roll)), None)
    if rec:
        st.json(rec)
        st.write("You can only view your record. Contact admin for changes.")
    else:
        st.error("Record not found (strange). Contact admin.")

# ---------- Public message ----------
else:
    st.info("Please login as Admin or Student to continue.")

# Footer with college & author
st.write("---")
st.markdown(f"**{COLLEGE_NAME}**  •  App by {AUTHOR_NAME} (Roll: {AUTHOR_ROLL})")
