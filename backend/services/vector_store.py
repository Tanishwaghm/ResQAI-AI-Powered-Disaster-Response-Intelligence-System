"""
ResQAI - Vector Store Service (ChromaDB)
Handles embedding storage, retrieval, and semantic search.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K_RESULTS,
)

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages ChromaDB vector storage for the ResQAI knowledge base.
    Supports adding documents, semantic search, and collection management.
    """

    def __init__(self):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"VectorStore initialized. Collection: {CHROMA_COLLECTION_NAME}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        source_name: str,
    ) -> int:
        """
        Add chunked document texts to ChromaDB.
        Returns the number of chunks added.
        """
        if not texts:
            return 0

        embeddings = self.embed_texts(texts)
        ids = [str(uuid.uuid4()) for _ in texts]

        # Stamp each chunk with source and timestamp
        timestamp = datetime.utcnow().isoformat()
        for meta in metadatas:
            meta["source"] = source_name
            meta["upload_time"] = timestamp

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(f"Added {len(texts)} chunks from '{source_name}' to ChromaDB.")
        return len(texts)

    def similarity_search(
        self, query: str, k: int = TOP_K_RESULTS
    ) -> List[Dict[str, Any]]:
        """
        Perform cosine similarity search against stored embeddings.
        Returns top-k results with text, metadata, and distance.
        """
        query_embedding = self.embed_texts([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, self.collection.count() or 1),
            include=["documents", "metadatas", "distances"],
        )

        if not results["documents"] or not results["documents"][0]:
            return []

        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # Convert cosine distance to similarity score (0-1)
            relevance = round(1 - dist, 4)
            output.append(
                {
                    "text": doc,
                    "metadata": meta,
                    "relevance_score": relevance,
                }
            )

        return output

    def get_all_sources(self) -> List[Dict[str, Any]]:
        """
        Return a deduplicated list of all source documents in the store.
        """
        if self.collection.count() == 0:
            return []

        all_items = self.collection.get(include=["metadatas"])
        sources: Dict[str, Dict] = {}

        for meta in all_items["metadatas"]:
            src = meta.get("source", "Unknown")
            if src not in sources:
                sources[src] = {
                    "name": src,
                    "chunk_count": 0,
                    "upload_time": meta.get("upload_time", ""),
                }
            sources[src]["chunk_count"] += 1

        return list(sources.values())

    def get_total_chunks(self) -> int:
        return self.collection.count()

    def health_check(self) -> str:
        try:
            count = self.collection.count()
            return f"OK ({count} chunks stored)"
        except Exception as e:
            return f"ERROR: {e}"
