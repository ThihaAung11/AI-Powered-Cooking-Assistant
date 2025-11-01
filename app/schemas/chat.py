from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message_id: int
    ai_reply: str
    cooking_recipe: Optional[str] = None
    language: str = "en"


class ChatHistoryItem(BaseModel):
    id: int
    user_message: str
    ai_reply: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryItem]
    total: int
