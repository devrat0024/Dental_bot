# AI Dental Health Assistant API 🦷

A robust, production-ready AI Assistant designed to provide sophisticated educational dental health information. Backed by FastAPI, strictly typed with Pydantic, secured with JWT authentication, and powered by Microsoft's `phi-2` LLM model.

## Features ✨

- **Constrained AI Intelligence**: Driven by a pre-loaded local Medical Guidelines context file, the assistant is bounded to provide professional, educational advice and strictly route diagnostics or emergencies to actual dental doctors.
- **JWT Security**: Secures endpoints to prevent unauthorized access.
- **FastAPI Powered**: Asynchronous endpoints, automatic Pydantic data validation, and built-in interactive Swagger UI.
- **HuggingFace & LangChain Integration**: Smoothly pipeline the `microsoft/phi-2` generative text model into reliable, production-ready inference endpoints.

---

## Architecture & Directory Structure 📁

- `api/`: Contains FastApi routing (`routes.py`).
- `auth/`: Houses JWT creation, payload decoding, and dependency injection logic (`jwt_handler.py`, `dependencies.py`).
- `context/`: Stores the bounded medical constraints logic (`medical_guidelines.txt`).
- `models/`: Centralized Pydantic schemas for request validation (`schemas.py`).
- `services/`: Encapsulates the Heavy LLM instantiation and generation logic (`llm_service.py`).
- `main.py`: The root Uvicorn/FastAPI entrypoint.

## Installation 🚀

### 1. Requirements

Ensure you have Python 3.9+ installed. You also need a machine with a capable CPU/GPU to run the `microsoft/phi-2` model locally.

### 2. Install Dependencies

Clone this repository and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Server

Launch the Uvicorn ASGI server:
```bash
uvicorn main:app --reload
```
You will see downloading indicators as the `phi-2` model initializes on the first run. The server runs on `http://localhost:8000`.

---

## Using the API 🌐

We highly recommend using the automatic Swagger UI for easy endpoint testing.

**1. Navigate to Docs:**
Go to [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

**2. Authentication (Login):**
- Click the green **Authorize** button.
- Use the trial credentials:
  - **Username:** `admin`
  - **Password:** `password123`
- Click `Authorize` to receive an active Bearer Token.

**3. Ask the Assistant:**
- Locate the **POST `/api/v1/ask`** route.
- Click **Try it out**.
- Submit a JSON payload, for example:
```json
{
  "question": "What is the proper way to treat a tooth that just got knocked out?"
}
```
- Execute the request to receive a safe, bounded response relying on the internal medical guidelines!

---

## Testing 🧪

A comprehensive Pytest suite enforces correct API behaviors, including unauthenticated blocking.

Run tests via:
```bash
python -m pytest test_main.py
```
