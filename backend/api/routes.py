from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.schemas import Token, ChatRequest, ChatResponse, TokenData
from auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.dependencies import get_current_user

router = APIRouter()

# Mock user database for demonstration purposes
MOCK_USER_DB = {
    "admin": {
        "username": "admin",
        "full_name": "Clinic Administrator",
        "hashed_password": "fakehashedpassword", # In real life, use Passlib to hash
        "password": "password123" # Mock plain text for testing
    }
}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = MOCK_USER_DB.get(form_data.username)
    if not user or form_data.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(
    request: ChatRequest, 
    current_user: TokenData = Depends(get_current_user)
):
    """
    Secure endpoint to ask the dental AI assistant questions.
    """
    # Import the service here to avoid holding up the initial FastAPI load if it takes a while
    from services.llm_service import llm_service
    
    try:
        answer = llm_service.get_dental_advice(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred generating the response: {str(e)}"
        )
