"""
ResQAI - RAG Service
Orchestrates retrieval, context injection, and LLM response generation.
Also handles emergency severity/category classification and confidence scoring.
"""

import logging
import re
from typing import List, Dict, Any, Tuple

from services.vector_store import VectorStore
from services.groq_service import GroqService
from models.response_models import Source

logger = logging.getLogger(__name__)

# ── System Prompts ─────────────────────────────────────────────────────────────

RAG_SYSTEM_PROMPT = """You are ResQAI, an expert AI emergency response assistant.
You provide life-saving guidance during disasters and emergencies.

RULES:
1. Always be calm, clear, and actionable.
2. Prioritize human safety above all else.
3. Use only the provided context to answer. If context is insufficient, say so clearly.
4. Provide step-by-step instructions when applicable.
5. Always recommend contacting official emergency services (call 112 in India).
6. Never speculate or fabricate emergency procedures.
7. Keep answers concise but complete.

Disaster types you handle: Flood, Earthquake, Fire, Cyclone, Landslide, Medical Emergency,
Building Collapse, Heat Wave.
"""

CLASSIFIER_SYSTEM_PROMPT = """You are an emergency classification AI.
Respond ONLY with the exact label requested — no explanations, no punctuation."""


class RAGService:
    """
    Retrieval-Augmented Generation pipeline for ResQAI.
    """

    def __init__(self, vector_store: VectorStore, groq_service: GroqService):
        self.vector_store = vector_store
        self.groq = groq_service

    # ── Classification ─────────────────────────────────────────────────────────

    def classify_severity(self, query: str, answer: str) -> str:
        """
        Classify emergency severity as LOW | MEDIUM | HIGH | CRITICAL.
        """
        prompt = f"""Given this emergency query and response, classify the severity.

Query: {query}
Response (first 300 chars): {answer[:300]}

Severity levels:
- CRITICAL: Immediate life threat, mass casualties, active danger
- HIGH: Serious injury risk, urgent action needed
- MEDIUM: Significant risk but manageable with care
- LOW: Precautionary, general preparedness

Respond with ONLY one word: CRITICAL, HIGH, MEDIUM, or LOW"""

        result = self.groq.single_shot(prompt, CLASSIFIER_SYSTEM_PROMPT)
        result = result.strip().upper()
        if result not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
            return "HIGH"
        return result

    def classify_category(self, query: str) -> str:
        """
        Classify emergency type: Flood | Earthquake | Fire | Cyclone | Medical | Other
        """
        prompt = f"""Classify this emergency query into ONE category.

Query: {query}

Categories: Flood, Earthquake, Fire, Cyclone, Medical, Landslide, Building Collapse, Heat Wave, Other

Respond with ONLY the category name."""

        result = self.groq.single_shot(prompt, CLASSIFIER_SYSTEM_PROMPT)
        valid = {
            "Flood", "Earthquake", "Fire", "Cyclone", "Medical",
            "Landslide", "Building Collapse", "Heat Wave", "Other"
        }
        result = result.strip().title()
        return result if result in valid else "Other"

    def compute_confidence(self, sources: List[Dict[str, Any]]) -> float:
        """
        Compute confidence score (0-100) based on retrieval quality.
        - No sources → 30 (LLM knowledge only)
        - Average relevance × 100, capped to 95
        """
        if not sources:
            return 30.0
        avg_relevance = sum(s["relevance_score"] for s in sources) / len(sources)
        return round(min(avg_relevance * 100, 95.0), 1)

    # ── Core RAG Pipeline ──────────────────────────────────────────────────────

    def answer(
        self,
        query: str,
        session_id: str = "default",
        use_rag: bool = True,
    ) -> Tuple[str, List[Source], float, str, str]:
        """
        Full RAG pipeline:
        1. Retrieve relevant chunks from ChromaDB
        2. Inject context into LLM prompt
        3. Generate answer
        4. Classify severity and category
        5. Return (answer, sources, confidence, severity, category)
        """
        retrieved: List[Dict[str, Any]] = []

        if use_rag and self.vector_store.get_total_chunks() > 0:
            retrieved = self.vector_store.similarity_search(query)

        # Build context block from retrieved chunks
        context_block = ""
        if retrieved:
            context_parts = []
            for i, r in enumerate(retrieved, 1):
                src = r["metadata"].get("filename", "document")
                pg = r["metadata"].get("page", "?")
                context_parts.append(
                    f"[Source {i}: {src}, Page {pg}]\n{r['text']}"
                )
            context_block = "\n\n---\n\n".join(context_parts)

        # Compose user prompt
        if context_block:
            user_prompt = f"""Use the following verified emergency knowledge to answer the question.

CONTEXT:
{context_block}

QUESTION: {query}

Provide a clear, actionable, step-by-step response."""
        else:
            user_prompt = f"""Answer this emergency question using your expert knowledge.
No verified documents were found in the knowledge base for this query.
Be clear about this limitation and still provide the best guidance possible.

QUESTION: {query}"""

        # LLM call with memory
        answer_text = self.groq.chat(
            user_message=user_prompt,
            system_prompt=RAG_SYSTEM_PROMPT,
            session_id=session_id,
        )

        # Build Source objects
        sources: List[Source] = []
        for r in retrieved:
            sources.append(
                Source(
                    document_name=r["metadata"].get("filename", "Unknown"),
                    page=r["metadata"].get("page"),
                    chunk_preview=r["text"][:200] + "...",
                    relevance_score=round(r["relevance_score"] * 100, 1),
                )
            )

        confidence = self.compute_confidence(retrieved)
        severity = self.classify_severity(query, answer_text)
        category = self.classify_category(query)

        return answer_text, sources, confidence, severity, category
