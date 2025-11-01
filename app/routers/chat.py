from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse, ChatHistoryItem
from ..services.chat_service import chat_with_cooking_assistant, get_chat_history
from ..deps import get_current_user
from ..models import User

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the cooking assistant and get AI response
    """
    try:
        result = chat_with_cooking_assistant(
            user_id=current_user.id,
            user_message=payload.message,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")


@router.get("/history", response_model=ChatHistoryResponse)
def get_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for the current user
    """
    messages = get_chat_history(
        user_id=current_user.id,
        db=db,
        limit=limit
    )
    return {
        "messages": messages,
        "total": len(messages)
    }
