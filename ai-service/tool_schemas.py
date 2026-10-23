# ai-service/tool_schemas.py

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_clinical_knowledge",
            "description": "Search for clinical knowledge, doctors, clinics, and treatment details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query, e.g., 'knee pain doctor' or 'flu vaccine instructions'."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_patient_bookings",
            "description": "Retrieve the list of existing appointments for the patient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The ID of the patient. Default is P001."
                    }
                },
                "required": ["patient_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Create a new appointment for the patient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {"type": "string", "description": "The ID of the doctor."},
                    "treatment_id": {"type": "string", "description": "The ID of the treatment."},
                    "booking_date": {"type": "string", "description": "Date in YYYY-MM-DD format."},
                    "booking_time": {"type": "string", "description": "Time in HH:MM:SS format."}
                },
                "required": ["doctor_id", "treatment_id", "booking_date", "booking_time"]
            }
        }
    }
]