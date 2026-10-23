# backend/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's input message")
    patient_id: str = Field(default="P001", description="The patient ID")
    history: Optional[List[Message]] = Field(default_factory=list, description="Previous conversation history")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="The AI assistant's response")

class BookingItem(BaseModel):
    booking_id: str
    doctor_name: str
    treatment_name: str
    booking_date: str
    booking_time: str
    status: str

class BookingListResponse(BaseModel):
    bookings: List[BookingItem]