"""
ResQAI - Response Pydantic Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Source(BaseModel):
    document_name: str
    page: Optional[int] = None
    chunk_preview: str
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str
    confidence_score: float = Field(..., ge=0.0, le=100.0)
    severity: str = Field(..., description="LOW | MEDIUM | HIGH | CRITICAL")
    category: str = Field(..., description="Flood | Earthquake | Fire | Cyclone | Medical | Other")
    sources: List[Source] = []
    session_id: str
    rag_used: bool


class AgentChatResponse(BaseModel):
    answer: str
    agent_used: str = Field(..., description="Which agent handled the query")
    agent_explanation: str = Field(..., description="Why this agent was selected")
    confidence_score: float = Field(..., ge=0.0, le=100.0)
    severity: str
    category: str
    sources: List[Source] = []
    session_id: str


class DocumentInfo(BaseModel):
    id: str
    name: str
    chunk_count: int
    upload_time: Optional[str] = None


class DocumentsResponse(BaseModel):
    documents: List[DocumentInfo]
    total_chunks: int


class UploadResponse(BaseModel):
    success: bool
    filename: str
    chunks_created: int
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    chroma_status: str
    groq_status: str
    embedding_model: str
