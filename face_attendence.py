
import cv2
import face_recognition
import numpy as np
import mysql.connector
import pickle
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import traceback

# Email Configuration
EMAIL_SENDER = " "  # Replace with your email
EMAIL_PASSWORD = " "  # Replace with your email password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ✅ MySQL Connection
def create_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=" ",  # Replace with your password
        database=" "# Replace with your database name
    )

# ✅ Fetch face encodings from the database
def fetch_face_encodings():
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, face_encoding, email, category, mobile_number FROM person_records")
    face_data = cursor.fetchall()
    conn.close()

    ids, encodings, names, emails, categories, mobile_numbers = [], [], [], [], [], []
    for row in face_data:
        id, name, encoding_blob, email, category, mobile_number = row
        try:
            encoding = pickle.loads(encoding_blob)
            if len(encoding) != 128:
                print(f"⚠️ Warning: Invalid encoding for {name}, skipping.")
                continue
            ids.append(id)
            encodings.append(encoding)
            names.append(name)
            emails.append(email)
            categories.append(category)
            mobile_numbers.append(mobile_number)
        except Exception as e:
            print(f"❌ Error decoding face encoding for {name}: {e}")
            continue

    print(f"✅ Loaded {len(encodings)} face encodings from database.")
    return ids, encodings, names, emails, categories, mobile_numbers

# ✅ Get last scan time and status
def get_last_scan_time(name):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, last_scan_time FROM person_records WHERE name = %s", (name,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)

# ✅ Update status and last scan time
def update_status(name, status):
    conn = create_db_connection()
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE person_records SET status = %s, last_scan_time = %s WHERE name = %s",
                   (status, current_time, name))
    conn.commit()
    conn.close()

# ✅ Mark attendance
def mark_attendance(name, email, category, status, tree):
    conn = create_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    time_now = now.strftime("%H:%M:%S")
    date_now = now.strftime("%Y-%m-%d")

    cursor.execute("SELECT mobile_number FROM person_records WHERE name = %s", (name,))
    result = cursor.fetchone()
    mobile_number = result[0] if result else "N/A"

    cursor.execute(
        "INSERT INTO attendance (name, mobile_number, email, status, category, date, time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (name, mobile_number, email, status, category, date_now, time_now)
    )
    conn.commit()
    conn.close()

    display_attendance_data(tree)

# ✅ Email notification
def send_email(to_email, name, status):
    now = datetime.now()
    subject = "Face Recognition Attendance System"
    message = f"""Hello {name},

Your attendance status has been updated to: {status}.
Date: {now.strftime("%Y-%m-%d")}
Time: {now.strftime("%H:%M:%S")}

Best Regards,
Attendance System
"""

    try:
        print(f"📧 Sending email to {to_email}...")
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()

        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email failed: {e}")

# ✅ Face recognition
def recognize_faces(ids, encodings, names, emails, categories, mobile_numbers, tree):
    cap = None
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("❌ Camera not accessible.")
            messagebox.showerror("Camera Error", "Could not access the camera.")
            return

        print("📷 Starting video capture... Press 'q' to quit.")
        cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)

        while True:
            success, img = cap.read()
            if not success:
                print("❌ Failed to capture frame.")
                break

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img_rgb)
            encodes_in_frame = face_recognition.face_encodings(img_rgb, face_locations)

            for encode_face, location in zip(encodes_in_frame, face_locations):
                matches = face_recognition.compare_faces(encodings, encode_face, tolerance=0.55)
                face_distances = face_recognition.face_distance(encodings, encode_face)
                best_match_index = np.argmin(face_distances)

                if best_match_index != -1 and matches[best_match_index]:
                    name = names[best_match_index]
                    current_status, last_time = get_last_scan_time(name)
                    if last_time and datetime.now() - last_time < timedelta(seconds=60):
                        print(f"⏳ Skipping {name}, scanned recently.")
                        continue

                    new_status = "Out" if current_status == "In" else "In"
                    update_status(name, new_status)
                    mark_attendance(name, emails[best_match_index], categories[best_match_index], new_status, tree)
                    send_email(emails[best_match_index], name, new_status)
                    label = f"{name} ({new_status})"
                    color = (0, 255, 0) if new_status == "In" else (0, 0, 255)
                else:
                    label = "Unknown"
                    color = (0, 0, 255)

                top, right, bottom, left = location
                cv2.rectangle(img, (left, top), (right, bottom), color, 2)
                cv2.putText(img, label, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            cv2.imshow("Face Recognition", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"❌ Face recognition error: {e}")
        traceback.print_exc()

    finally:
        if cap: cap.release()
        cv2.destroyAllWindows()
        print("🛑 Stopped video capture.")

# ✅ Start face recognition thread
def start_face_recognition(tree):
    ids, encs, names, emails, categories, mobiles = fetch_face_encodings()
    if len(encs) == 0:
        print("⚠️ No encodings found.")
        return
    recognize_faces(ids, encs, names, emails, categories, mobiles, tree)

# ✅ Fetch attendance records
def fetch_attendance_data():
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, mobile_number, status, category, date, time FROM attendance ORDER BY date DESC, time DESC")
    data = cursor.fetchall()
    conn.close()
    print("Fetched Data:", data)
    return data

def display_attendance_data(tree, search=""):
    # Clear the tree
    for row in tree.get_children():
        tree.delete(row)

    data = fetch_attendance_data()
    print(f"🔍 Search Query: '{search}'")

    if search:
        search = search.strip().lower()
        filtered = [r for r in data if search in r[1].lower()]
    else:
        filtered = data

    if not filtered:
        print("⚠️ No match found for search.")
        show_temp_popup("Data not found")

    for r in filtered[::-1]:
        print("📥 Displaying:", r)
        tree.insert("", "end", values=r)


# ✅ Popup if no data
def show_temp_popup(message):
    popup = tk.Toplevel()
    popup.title("Search Result")
    popup.geometry("250x100")
    tk.Label(popup, text=message, font=("Arial", 12)).pack(pady=20)
    popup.after(2000, popup.destroy)

# ✅ Handle search
def on_search(event, tree, entry):
    q = entry.get().strip()
    display_attendance_data(tree, q)

def refresh_data(tree):
    display_attendance_data(tree)
    messagebox.showinfo("Refresh", "Data has been refreshed.")

# ✅ Main GUI
def create_gui():
    window = tk.Tk()
    window.title("Face Recognition Attendance")
    window.geometry("850x550")

    tk.Label(window, text="Face Recognition Attendance System", font=("Arial", 16)).pack(pady=10)

    frame = tk.Frame(window)
    frame.pack(pady=5)

    tk.Label(frame, text="Search Name:", font=("Arial", 12)).pack(side="left", padx=5)
    search_entry = tk.Entry(frame, font=("Arial", 12), width=30)
    search_entry.pack(side="left", padx=5)
    refresh_btn = tk.Button(frame, text="Refresh", font=("Arial", 12), command=lambda: refresh_data(tree))
    refresh_btn.pack(side="left", padx=5)

    columns = ("ID", "Name", "Mobile Number", "Status", "Category", "Date", "Time")
    tree = ttk.Treeview(window, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    tree.pack(pady=10, fill="both", expand=True)

    display_attendance_data(tree)

    search_entry.bind("<Return>", lambda e: on_search(e, tree, search_entry))

    # Run face recognition in thread
    thread = threading.Thread(target=start_face_recognition, args=(tree,), daemon=True)
    thread.start()

    window.mainloop()

# ✅ Run the app
if __name__ == "__main__":
    create_gui()
