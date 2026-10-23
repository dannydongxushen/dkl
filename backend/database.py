# backend/database.py
import os
import sys
import sqlite3
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import config

DB_FILE = config["paths"]["sqlite_db"]

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_patient_context(patient_id: str) -> dict:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, known_allergies FROM patients WHERE patient_id = ?", (patient_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": patient_id,
                "name": f"{row['first_name']} {row['last_name']}",
                "allergies": row['known_allergies']
            }
    except Exception as e:
        print(f"Error fetching patient context: {e}")
        
    return {"id": patient_id, "name": "Unknown", "allergies": "None"}

def get_patient_bookings(patient_id: str) -> list:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, b.booking_date, b.booking_time, b.status, 
                   d.full_name as doctor_name, t.treatment_name
            FROM patient_bookings b
            JOIN doctors d ON b.doctor_id = d.doctor_id
            JOIN treatments t ON b.treatment_id = t.treatment_id
            WHERE b.patient_id = ?
            ORDER BY b.booking_date, b.booking_time
        """, (patient_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Database error in get_patient_bookings: {e}")
        return []

def create_booking(patient_id: str, doctor_id: str, treatment_id: str, booking_date: str, booking_time: str) -> str:
    booking_id = f"B{str(uuid.uuid4().int)[:6]}"
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patient_bookings (booking_id, patient_id, doctor_id, treatment_id, booking_date, booking_time, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'Confirmed', 'Created by AI')
        """, (booking_id, patient_id, doctor_id, treatment_id, booking_date, booking_time))
        conn.commit()
        conn.close()
        return f"Booking successfully created with ID {booking_id}."
    except Exception as e:
        return f"Failed to create booking: {str(e)}"