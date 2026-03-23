# DentaFlow AI: Intelligent Dental Care Assistant

DentaFlow AI is a comprehensive dental care ecosystem featuring a multi-turn triage chatbot, role-based dashboards for patients and doctors, and a persistent medical record system. It uses Retrieval-Augmented Generation (RAG) to provide accurate, clinical-standard dental advice.

## 🚀 Key Features

*   **Intelligent Triage**: A stateful AI assistant that gathers symptoms (pain level, duration, swelling, etc.) interactive style before providing advice.
*   **Multi-User Persistence**: Full SQLite database integration to store users, appointments, and chat histories.
*   **Multi-Doctor Architecture**: Independent dashboards for doctors with isolated patient data and scheduling.
*   **Secure Authentication**: PBKDF2 password hashing and JWT-based session management.
*   **Clinical RAG Pipeline**: Powered by FAISS and Sentence Transformers for accurate dental guidelines retrieval.

## 🛠️ Tech Stack

*   **Backend**: FastAPI, SQLAlchemy, SQLite, Pydantic, Passlib, Python-Jose.
*   **Frontend**: React, TypeScript, TailwindCSS (Vanilla CSS logic), Framer Motion, Lucide-React.
*   **AI/LLM**: Sentence-Transformers (Local), FAISS (Vector DB).

## 📦 Setup & Installation

### Prerequisites
*   Python 3.8+
*   Node.js 16+

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
   ```

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## 🔐 Configuration
- **API Port**: The system is pre-configured to run the backend on port `8002`.
- **Secret Key**: You can update the `SECRET_KEY` in `backend/main.py` for production deployment.

## 📄 License
MIT License - 2026 DentaFlow AI Team
