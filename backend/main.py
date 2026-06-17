"""
ResQAI - FastAPI Main Application
Entry point for the AI Disaster Response Intelligence System backend.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import (
    APP_TITLE, APP_VERSION, APP_DESCRIPTION,
    ALLOWED_ORIGINS, MAX_PDF_SIZE_MB, PDF_UPLOAD_DIR
)
from models.request_models import ChatRequest, AgentChatRequest
from models.response_models import (
    ChatResponse, AgentChatResponse, DocumentsResponse,
    DocumentInfo, UploadResponse, HealthResponse
)
from services.vector_store import VectorStore
from services.groq_service import GroqService
from services.rag_service import RAGService
from services.pdf_loader import PDFLoader
from services.agent_router import AgentRouter

# ── Logging Setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Global Services (initialized at startup) ──────────────────────────────────
vector_store: VectorStore = None
groq_service: GroqService = None
rag_service: RAGService = None
pdf_loader: PDFLoader = None
agent_router: AgentRouter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all services on startup."""
    global vector_store, groq_service, rag_service, pdf_loader, agent_router

    logger.info("🚀 Starting ResQAI backend...")
    os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)

    vector_store = VectorStore()
    groq_service = GroqService()
    rag_service = RAGService(vector_store, groq_service)
    pdf_loader = PDFLoader()
    agent_router = AgentRouter(groq_service)

    logger.info("✅ All services initialized successfully.")
    yield
    logger.info("🛑 ResQAI backend shutting down.")


# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "ResQAI",
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse(
        status="healthy",
        version=APP_VERSION,
        chroma_status=vector_store.health_check(),
        groq_status=groq_service.health_check(),
        embedding_model="all-MiniLM-L6-v2",
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    RAG-powered emergency chat endpoint.
    Retrieves relevant knowledge and generates a contextual response.
    """
    try:
        answer, sources, confidence, severity, category = rag_service.answer(
            query=request.message,
            session_id=request.session_id,
            use_rag=request.use_rag,
        )
        return ChatResponse(
            answer=answer,
            confidence_score=confidence,
            severity=severity,
            category=category,
            sources=sources,
            session_id=request.session_id,
            rag_used=request.use_rag and vector_store.get_total_chunks() > 0,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent-chat", response_model=AgentChatResponse, tags=["Agents"])
async def agent_chat(request: AgentChatRequest):
    """
    Multi-agent emergency chat endpoint.
    Routes query to the most appropriate specialist agent.
    """
    try:
        # Retrieve RAG context first
        retrieved = []
        context = ""
        if vector_store.get_total_chunks() > 0:
            retrieved = vector_store.similarity_search(request.message)
            if retrieved:
                context = "\n\n".join(
                    [f"[{r['metadata'].get('filename','doc')}]\n{r['text']}" for r in retrieved]
                )

        answer, agent_name, explanation = agent_router.respond(
            query=request.message,
            session_id=request.session_id,
            force_agent=request.force_agent,
            context=context,
        )

        # Classification
        severity = rag_service.classify_severity(request.message, answer)
        category = rag_service.classify_category(request.message)
        confidence = rag_service.compute_confidence(retrieved)

        from models.response_models import Source
        sources = [
            Source(
                document_name=r["metadata"].get("filename", "Unknown"),
                page=r["metadata"].get("page"),
                chunk_preview=r["text"][:200] + "...",
                relevance_score=round(r["relevance_score"] * 100, 1),
            )
            for r in retrieved
        ]

        return AgentChatResponse(
            answer=answer,
            agent_used=agent_name,
            agent_explanation=explanation,
            confidence_score=confidence,
            severity=severity,
            category=category,
            sources=sources,
            session_id=request.session_id,
        )
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-pdf", response_model=UploadResponse, tags=["Documents"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF to the knowledge base.
    Parses, chunks, embeds, and stores in ChromaDB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_PDF_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_PDF_SIZE_MB} MB.",
        )

    try:
        file_path = pdf_loader.save_uploaded_file(content, file.filename)
        texts, metadatas = pdf_loader.load_and_chunk(file_path)
        chunks_added = vector_store.add_documents(texts, metadatas, file.filename)

        return UploadResponse(
            success=True,
            filename=file.filename,
            chunks_created=chunks_added,
            message=f"Successfully processed '{file.filename}' into {chunks_added} searchable chunks.",
        )
    except Exception as e:
        logger.error(f"PDF upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=DocumentsResponse, tags=["Documents"])
async def get_documents():
    """List all documents in the knowledge base."""
    try:
        sources = vector_store.get_all_sources()
        docs = [
            DocumentInfo(
                id=str(i),
                name=s["name"],
                chunk_count=s["chunk_count"],
                upload_time=s.get("upload_time", ""),
            )
            for i, s in enumerate(sources)
        ]
        return DocumentsResponse(
            documents=docs,
            total_chunks=vector_store.get_total_chunks(),
        )
    except Exception as e:
        logger.error(f"Documents fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
