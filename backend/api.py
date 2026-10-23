# backend/api.py
import os
import sys
from fastapi import APIRouter, HTTPException

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_SERVICE_DIR = os.path.join(BASE_DIR, "ai-service")
sys.path.append(BASE_DIR)
sys.path.append(AI_SERVICE_DIR)

from schemas import ChatRequest, ChatResponse, BookingListResponse
import database
from agent_core import process_message

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.history]
        messages.append({"role": "user", "content": request.message})
        
        reply = process_message(messages=messages, patient_id=request.patient_id)
        
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookings", response_model=BookingListResponse)
async def get_bookings(patient_id: str = "P001"):
    try:
        bookings_data = database.get_patient_bookings(patient_id)
        return BookingListResponse(bookings=bookings_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))