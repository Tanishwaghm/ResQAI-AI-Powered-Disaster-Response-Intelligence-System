"""
ResQAI - Request Pydantic Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(default="default", description="Session ID for memory")
    use_rag: Optional[bool] = Field(default=True, description="Whether to use RAG pipeline")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What should I do during a flood?",
                "session_id": "user_123",
                "use_rag": True
            }
        }


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(default="default", description="Session ID for memory")
    force_agent: Optional[str] = Field(
        default=None,
        description="Force routing to a specific agent: medical, rescue, navigation, communication"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Someone is bleeding heavily, what first aid should I give?",
                "session_id": "user_123",
                "force_agent": None
            }
        }
