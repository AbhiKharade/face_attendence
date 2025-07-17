# Face & QR Code Based Attendance System with Email Notifications 📷📩

## 📌 Project Description

This project is a **smart attendance system** that uses **Face Recognition** and **QR Code scanning** to mark attendance. It features a **Tkinter-based GUI** and automatically sends **email notifications** (with name, date, time, and location) to the user's **mobile/email**. It also exports attendance data to an **Excel sheet** and stores it in a **MySQL database**.

---

## 🛠️ Technologies Used

- **Python 3**
- **OpenCV** – Face Detection & Recognition
- **face_recognition** – Face Encoding and Matching
- **MySQL** – Attendance Data Storage
- **Tkinter** – Graphical User Interface
- **qrcode / pyzbar** – QR Code Scanning
- **smtplib / email** – Email Notification
- **pandas / openpyxl** – Excel Export
- **geocoder / geopy** – Location Capture (Optional)

---

## 📋 Features

- ✅ Face Recognition for Attendance
- ✅ QR Code Scanning
- ✅ Tkinter GUI with 'Temp In / Out' buttons
- ✅ Email sent with:
  - Name
  - Date & Time
  - Location
- ✅ MySQL Database Storage
- ✅ Attendance Export to Excel
- ✅ Live camera preview for scanning
- ✅ Error handling (no face found, duplicate entry, etc.)

---

## 🖼️ GUI Overview

- **Main Window:** Contains:
  - "Start QR Scan"
  - "Temp In" / "Temp Out" button
- **Face Recognition Window:** Captures face when Temp In/Out is selected
- **Status Labels:** Shows attendance marked, errors, and email sent status

---


---

## ✅ Requirements

Install all required libraries:

```bash
pip install opencv-python face_recognition pyzbar mysql-connector-python pandas openpyxl geocoder


