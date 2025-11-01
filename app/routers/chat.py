from fastapi import APIRouter, HTTPException, Query

from ..schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from ..services.chat_service import chat_with_cooking_assistant, get_chat_history
from ..deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    db: SessionDep,
    current_user: CurrentUser
):
    """
    Send a message to the cooking assistant and get AI response.
    
    The AI assistant can:
    - Recommend recipes based on your preferences
    - Provide cooking guidance and step-by-step instructions
    - Answer cooking-related questions
    - Respond in your preferred language (English or Burmese)
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
    db: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100, description="Number of messages to retrieve")
):
    """
    Get chat history for the current user.
    
    Returns the most recent chat messages in chronological order.
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
