
import cv2
import face_recognition
import mysql.connector
import pickle

# Database connection
def create_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=" 1",  # ✅ Replace with your password
        database=" "# Replace with your database name
    )

# Load image and extract face encoding
def get_face_encoding(image_path):
    img = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(img)
    if len(encodings) == 0:
        raise Exception("❌ No face detected in the image.")
    return encodings[0]

# Insert into database
def insert_person(name, category, email, mobile_number, image_path):
    try:
        encoding = get_face_encoding(image_path)
        encoding_blob = pickle.dumps(encoding)

        conn = create_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO person_records (name, category, email, mobile_number, face_encoding, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (name, category, email, mobile_number, encoding_blob, "In")
        cursor.execute(sql, values)

        conn.commit()
        conn.close()
        print(f"✅ Person '{name}' inserted successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")

# Example usage
if __name__ == "__main__":
    name = ""
    category = " "
    email = " "
    mobile_number = ""
    image_path = ""  # Replace with your image path

    insert_person(name, category, email, mobile_number, image_path)
