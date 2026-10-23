# ai-service/agent_core.py
import os
import sys
import json
import uuid
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from llm import llm_instance
from rag_engine import rag_engine_instance
from agent_prompts import build_system_prompt
from tool_schemas import TOOLS

DB_FILE = config["paths"]["sqlite_db"]

def get_patient_context(patient_id: str) -> dict:
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
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

def execute_tool(tool_name: str, args: dict, current_patient_id: str) -> str:
    if tool_name == "search_clinical_knowledge":
        query = args.get("query")
        docs = rag_engine_instance.search(query)
        if not docs:
            return "No relevant information found."
        return "\n\n".join([d["text"] for d in docs])
        
    elif tool_name == "get_patient_bookings":
        pid = args.get("patient_id", current_patient_id)
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.booking_date, b.booking_time, b.status, d.full_name as doctor, t.treatment_name as treatment
                FROM patient_bookings b
                JOIN doctors d ON b.doctor_id = d.doctor_id
                JOIN treatments t ON b.treatment_id = t.treatment_id
                WHERE b.patient_id = ?
            """, (pid,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "No bookings found."
            return json.dumps([dict(row) for row in rows])
        except Exception as e:
            return f"Database error: {str(e)}"
        
    elif tool_name == "create_booking":
        doc_id = args.get("doctor_id")
        treat_id = args.get("treatment_id")
        date = args.get("booking_date")
        time = args.get("booking_time")
        booking_id = f"B{str(uuid.uuid4().int)[:6]}"
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patient_bookings (booking_id, patient_id, doctor_id, treatment_id, booking_date, booking_time, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, 'Confirmed', 'Created by AI')
            """, (booking_id, current_patient_id, doc_id, treat_id, date, time))
            conn.commit()
            conn.close()
            return f"Booking successfully created with ID {booking_id}."
        except Exception as e:
            return f"Failed to create booking: {str(e)}"
            
    return "Unknown tool."

def process_message(messages: list, patient_id: str = "P001") -> str:
    patient_ctx = get_patient_context(patient_id)
    system_prompt = build_system_prompt(
        patient_id=patient_ctx["id"],
        patient_name=patient_ctx["name"],
        patient_allergies=patient_ctx["allergies"]
    )
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    while True:
        response = llm_instance.chat(messages=full_messages, tools=TOOLS)
        response_message = response.choices[0].message
        
        if not response_message.tool_calls:
            return response_message.content
            
        full_messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                function_args = {}
                
            tool_result = execute_tool(function_name, function_args, patient_ctx["id"])
            
            full_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result
            })