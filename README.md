# ResQAI — AI-Powered Disaster Response Intelligence System

> **Author:** Tanishka Hemant Waghmare  
> Final-Year AI & Data Science Project | LLM + RAG + Multi-Agent System

---

## Overview

ResQAI is an intelligent emergency response assistant that combines **Retrieval-Augmented Generation (RAG)**, **Multi-Agent AI**, and **LLMs** to provide real-time, contextual guidance during disasters. It retrieves verified information from uploaded emergency PDFs and generates actionable, life-saving responses.

---

## Problem Statement

During disasters, people face critical information gaps:
- What immediate actions to take?
- Whom to contact?
- What medical steps are required?
- How severe is the situation?

ResQAI solves this by acting as an intelligent, always-available emergency assistant trained on verified disaster response knowledge.

---

## Features

| Feature | Description |
|---|---|
| RAG Pipeline | Retrieves from PDF knowledge base before answering |
| Multi-Agent System | Routes queries to specialist agents (Medical, Rescue, Navigation, Communication) |
| Severity Classification | CRITICAL / HIGH / MEDIUM / LOW |
| Category Detection | Flood, Earthquake, Fire, Cyclone, Medical, etc. |
| Confidence Score | 0–100% based on retrieval relevance |
| PDF Knowledge Base | Upload any disaster management PDF |
| Conversation Memory | Multi-turn session-based memory |
| Source Citations | Shows which document chunk answered the query |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                         │
│              React + Tailwind CSS (Port 5173)               │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP (Axios)
┌───────────────────────▼─────────────────────────────────────┐
│                   FastAPI BACKEND (Port 8000)                │
│                                                             │
│  ┌──────────────┐   ┌────────────────┐  ┌───────────────┐  │
│  │  /chat       │   │  /agent-chat   │  │ /upload-pdf   │  │
│  │  RAG Mode    │   │  Agent Mode    │  │ /documents    │  │
│  └──────┬───────┘   └───────┬────────┘  └───────┬───────┘  │
│         │                   │                   │           │
│  ┌──────▼───────────────────▼──┐    ┌──────────▼────────┐  │
│  │       RAG Service           │    │    PDF Loader     │  │
│  │  (Retrieve + Generate)      │    │  (Chunk + Embed)  │  │
│  └──────────────┬──────────────┘    └────────┬──────────┘  │
│                 │                            │              │
│  ┌──────────────▼─────────────────────────── ▼──────────┐  │
│  │              ChromaDB Vector Store                   │  │
│  │          (all-MiniLM-L6-v2 embeddings)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                 │                                           │
│  ┌──────────────▼─────────────────────────────────────┐    │
│  │              COORDINATOR AGENT (Router)             │    │
│  │   Keyword scoring + LLM-based routing               │    │
│  └────┬───────────┬───────────────┬──────────────┬────┘    │
│       │           │               │              │          │
│  ┌────▼──┐  ┌────▼──┐  ┌────────▼─┐  ┌────────▼────┐     │
│  │Medical│  │Rescue │  │Navigation│  │Communication│     │
│  │Agent  │  │Agent  │  │Agent     │  │Agent        │     │
│  └───────┘  └───────┘  └──────────┘  └─────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Groq API — Llama 3.3 70B                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
ResQAI/
├── backend/
│   ├── main.py                  # FastAPI app, all endpoints
│   ├── config.py                # Environment variable settings
│   ├── requirements.txt
│   ├── .env.example
│   ├── services/
│   │   ├── groq_service.py      # LLM calls + memory
│   │   ├── rag_service.py       # RAG pipeline + classification
│   │   ├── vector_store.py      # ChromaDB operations
│   │   ├── pdf_loader.py        # PDF parsing + chunking
│   │   └── agent_router.py      # Coordinator agent
│   ├── agents/
│   │   ├── medical_agent.py
│   │   ├── rescue_agent.py
│   │   ├── navigation_agent.py
│   │   └── communication_agent.py
│   ├── models/
│   │   ├── request_models.py
│   │   └── response_models.py
│   └── data/
│       ├── pdfs/                # Uploaded PDFs stored here
│       └── chroma_db/           # Vector DB persisted here
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatBox.jsx
    │   │   ├── MessageBubble.jsx
    │   │   ├── Sidebar.jsx
    │   │   └── UploadPDF.jsx
    │   ├── pages/
    │   │   └── Home.jsx
    │   ├── services/
    │   │   └── api.js
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── postcss.config.js
```

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

---

### Backend Setup

```bash
cd ResQAI/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and add your GROQ_API_KEY

# Run backend
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

---

### Frontend Setup

```bash
cd ResQAI/frontend

npm install

# Optional: configure API URL
cp .env.example .env

npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | **required** | Your Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | ChromaDB storage path |
| `CHUNK_SIZE` | `1000` | PDF chunk size in characters |
| `CHUNK_OVERLAP` | `200` | Chunk overlap in characters |
| `TOP_K_RESULTS` | `5` | Number of RAG results to retrieve |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root info |
| `GET` | `/health` | Service health check |
| `POST` | `/chat` | RAG-powered emergency chat |
| `POST` | `/agent-chat` | Multi-agent emergency chat |
| `POST` | `/upload-pdf` | Upload PDF to knowledge base |
| `GET` | `/documents` | List all indexed documents |

### Example: POST /chat

```json
{
  "message": "What should I do during a flood?",
  "session_id": "user_123",
  "use_rag": true
}
```

Response:
```json
{
  "answer": "During a flood: 1. Move to higher ground immediately...",
  "confidence_score": 87.3,
  "severity": "HIGH",
  "category": "Flood",
  "sources": [...],
  "session_id": "user_123",
  "rag_used": true
}
```

---

## Resume Description

**ResQAI — AI Disaster Response Intelligence System**

Built a full-stack multi-agent AI system for disaster response using RAG, LangChain, ChromaDB, and Groq's Llama 3.3 70B. Implemented a coordinator agent that dynamically routes emergency queries to specialist agents (Medical, Rescue, Navigation, Communication), semantic PDF search via sentence-transformers embeddings, and real-time severity/category classification — all served through a FastAPI backend with a React + Tailwind frontend.

**Technologies:** Python · FastAPI · LangChain · ChromaDB · Sentence Transformers · Groq API · Llama 3.3 70B · React · Tailwind CSS · RAG · Multi-Agent Systems

---

## Interview Q&A

**Q: What is RAG and why did you use it?**  
A: RAG (Retrieval-Augmented Generation) combines semantic search over a vector database with LLM generation. I used it so ResQAI answers from verified emergency PDFs rather than hallucinating — critical for life-safety applications.

**Q: How does the multi-agent routing work?**  
A: The Coordinator Agent scores each query against keyword sets per agent. If scores are ambiguous, it falls back to an LLM routing call. The winning agent's specialized system prompt is then used for the final LLM call.

**Q: How are confidence scores calculated?**  
A: Based on the average cosine similarity score of retrieved chunks. No retrieved context → 30% (LLM only). Higher-relevance retrievals push toward 95%.

**Q: How does the vector search work?**  
A: PDFs are chunked with 1000-char size / 200-char overlap using LangChain's RecursiveCharacterTextSplitter, embedded with all-MiniLM-L6-v2 via Sentence Transformers, stored in ChromaDB, and retrieved via cosine similarity.

**Q: What disaster types does ResQAI support?**  
A: Flood, Earthquake, Fire, Cyclone, Landslide, Medical Emergency, Building Collapse, and Heat Wave.

---

## GitHub Repository

**Description:** AI-powered disaster response system combining RAG, multi-agent routing, and Llama 3.3 70B to provide real-time emergency guidance with PDF knowledge retrieval.

**Topics:** `ai` `rag` `llm` `multi-agent` `fastapi` `react` `chromadb` `langchain` `groq` `disaster-response` `emergency-ai` `sentence-transformers` `python` `tailwindcss`

---

## Future Scope

- Real-time disaster alerts via government APIs (NDMA, IMD)
- Voice interface for hands-free emergency use
- Multilingual support (Hindi, Marathi, etc.)
- Offline mode with quantized local LLMs
- Mobile app (React Native)
- Map integration for safe route visualization
- Integration with NDRF dispatch systems

---

## Screenshots

> Add screenshots here after running the project.

- `docs/screenshots/chat.png` — Main emergency chat interface  
- `docs/screenshots/agents.png` — Multi-agent mode  
- `docs/screenshots/upload.png` — PDF upload and knowledge base  

---

*Built by Tanishka Hemant Waghmare — AI & Data Science, B.Tech*
