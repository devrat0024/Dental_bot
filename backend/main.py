from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid
import os
from sqlalchemy.orm import Session
from jose import JWTError, jwt

# Local Imports
from auth.hasher import Hasher
from models import init_db, SessionLocal, User, ChatSession, ChatMessage, Appointment, MedicalNote
from schemas import UserSchema, AppointmentSchema, MedicalNoteSchema, ChatSessionSchema, ChatMessageSchema
from rag_pipeline.retrieval.search import RetrievalService
from rag_pipeline.response.generator import ResponseGenerator

# --- 0. CONFIG & INITIALIZATION ---

app = FastAPI(title="Dental AI Assistant Backend")

# Initialize DB on Startup
init_db()

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# RAG Services
retrieval_service = RetrievalService()
response_generator = ResponseGenerator()

# --- 1. AUTH SERVICE ---

SECRET_KEY = "super-secret-key-change-me"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserLogin(BaseModel):
    username: str
    password: str

class UserSignup(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    phone: Optional[str] = None
    role: Optional[str] = "patient"

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/signup", tags=["Auth"])
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    print(f"Signup attempt: {user_data.username}")
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            print("User already exists")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        print("Hashing password...")
        hashed_pw = Hasher.get_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_pw,
            full_name=user_data.full_name,
            email=user_data.email,
            phone_number=user_data.phone,
            role=user_data.role or "patient"
        )
        print(f"Creating user: {new_user.username} with role {new_user.role}")
        db.add(new_user)
        print("Committing to DB...")
        db.commit()
        print("Refreshing user...")
        db.refresh(new_user)
        print(f"User created with ID: {new_user.id}")
        return {"message": "User created successfully", "user_id": new_user.id}
    except Exception as e:
        print(f"Signup Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/login", tags=["Auth"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not Hasher.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "token_type": "bearer"}

@app.get("/profile", response_model=UserSchema, tags=["Auth"])
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# --- 2. CHAT SERVICE ---

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Fetch or Create Session
    session = None
    if request.conversation_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.conversation_id).first()
        if session and session.user_id != current_user.id:
            session = None # Don't allow accessing other's sessions
            
    if not session:
        session = ChatSession(user_id=current_user.id)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Get State from Session
    state = session.state or {"step": "INIT", "data": {}}
    
    try:
        # Step 1: Search context
        results = retrieval_service.search(request.question, k=3)
        
        # Step 2: Generate response (State-Aware)
        gen_result = response_generator.generate(request.question, results, state)
        answer = gen_result["answer"]
        
        # Step 3: Persistence
        # Store message
        user_msg = ChatMessage(session_id=session.id, role="user", content=request.question)
        bot_msg = ChatMessage(session_id=session.id, role="bot", content=answer)
        db.add_all([user_msg, bot_msg])
        
        # Update State
        if "new_state" in gen_result:
            session.state = gen_result["new_state"]
        
        db.commit()
        return {"answer": answer, "conversation_id": session.id}
        
    except Exception as e:
        print(f"Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. MEDICAL & APPOINTMENT SERVICES ---

@app.get("/dashboard/stats", tags=["Dashboard"])
async def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "doctor":
        total_patients = db.query(User).filter(User.role == "patient").count()
        today_appointments = db.query(Appointment).filter(Appointment.status == "scheduled").count()
        return {"total_patients": total_patients, "today_appointments": today_appointments}
    else:
        appointments = db.query(Appointment).filter(Appointment.patient_id == current_user.id).count()
        records = db.query(MedicalNote).filter(MedicalNote.patient_id == current_user.id).count()
        return {"appointments": appointments, "records": records}

@app.get("/appointments", response_model=List[AppointmentSchema], tags=["Appointments"])
async def list_appointments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "doctor":
        return db.query(Appointment).filter(Appointment.doctor_id == current_user.id).all()
    else:
        return db.query(Appointment).filter(Appointment.patient_id == current_user.id).all()

@app.post("/appointments", response_model=AppointmentSchema, tags=["Appointments"])
async def book_appointment(doctor_id: str, date_time: datetime, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can book appointments")
    
    appt = Appointment(patient_id=current_user.id, doctor_id=doctor_id, date_time=date_time)
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt

@app.get("/medical-records", response_model=List[MedicalNoteSchema], tags=["Medical Records"])
async def list_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(MedicalNote).filter(MedicalNote.patient_id == current_user.id).all()

@app.post("/medical-records", response_model=MedicalNoteSchema, tags=["Medical Records"])
async def add_record(patient_id: str, note: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can add medical notes")
    
    new_note = MedicalNote(patient_id=patient_id, doctor_id=current_user.id, note=note)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

# --- 5. NOTIFICATION SERVICE ---
# Placeholder for notifications

# --- 6. AI TRANSCRIPTION SERVICE ---
# Placeholder for voice/transcription logic

@app.post("/ai/transcribe", tags=["AI Service"])
async def transcribe_audio(audio_file_url: str):
    # Placeholder for Whisper integration
    return {
        "transcription": "Mock transcription: I have a severe toothache on my lower left molar.",
        "status": "success",
        "engine": "Whisper-v3-placeholder"
    }

# --- Root ---

@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Dental Enterprise API is online.",
        "services": ["User", "Chat", "Appointment", "Medical Records", "Notification", "AI"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
