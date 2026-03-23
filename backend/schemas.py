from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    full_name: str
    email: str
    role: str

class UserSchema(UserBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class ChatMessageSchema(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatSessionSchema(BaseModel):
    id: str
    user_id: str
    state: dict
    started_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AppointmentSchema(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    date_time: str
    status: str
    model_config = ConfigDict(from_attributes=True)

class MedicalNoteSchema(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    note: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
