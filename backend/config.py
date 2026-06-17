"""
ResQAI - Configuration Settings
Centralized configuration using environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq API ──────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.3"))

# ── Embedding Model ───────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "resqai_knowledge")

# ── PDF Upload ────────────────────────────────────────────────────────────────
PDF_UPLOAD_DIR: str = os.getenv("PDF_UPLOAD_DIR", "./data/pdfs")
MAX_PDF_SIZE_MB: int = int(os.getenv("MAX_PDF_SIZE_MB", "50"))

# ── RAG Settings ──────────────────────────────────────────────────────────────
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS: list = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

# ── App Meta ──────────────────────────────────────────────────────────────────
APP_TITLE: str = "ResQAI - AI Disaster Response Intelligence"
APP_VERSION: str = "1.0.0"
APP_DESCRIPTION: str = (
    "Multi-agent AI system for emergency response, disaster guidance, "
    "and real-time crisis intelligence powered by RAG and LLMs."
)
