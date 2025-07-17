CREATE TABLE person_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    email VARCHAR(100),
    mobile_number VARCHAR(15),
    face_encoding LONGBLOB NOT NULL,
    status VARCHAR(10),  -- e.g., 'In' or 'Out'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,               -- Foreign key from person_records.id
    name VARCHAR(100) NOT NULL,
    status VARCHAR(10),                   -- 'In' or 'Out'
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(255),                -- Optional: GPS or room number
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person_records(id)
);
