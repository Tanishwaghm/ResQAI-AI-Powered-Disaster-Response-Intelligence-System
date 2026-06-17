"""
ResQAI - PDF Loader & Text Chunker
Handles PDF parsing and recursive text splitting for RAG ingestion.
"""

import logging
import os
from typing import List, Dict, Any, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP, PDF_UPLOAD_DIR

logger = logging.getLogger(__name__)


class PDFLoader:
    """
    Loads PDFs, extracts text page-by-page, and splits into
    overlapping chunks suitable for embedding and retrieval.
    """

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)

    def load_and_chunk(
        self, file_path: str
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Load a PDF file and return:
        - texts: list of chunk strings
        - metadatas: list of dicts with page number and source filename
        """
        logger.info(f"Loading PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        if not pages:
            raise ValueError(f"PDF at {file_path} contains no extractable text.")

        # Split into chunks
        chunks = self.text_splitter.split_documents(pages)

        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            clean_text = chunk.page_content.strip()
            if not clean_text:
                continue
            texts.append(clean_text)
            metadatas.append(
                {
                    "page": chunk.metadata.get("page", 0) + 1,
                    "filename": os.path.basename(file_path),
                }
            )

        logger.info(
            f"PDF '{os.path.basename(file_path)}' → {len(pages)} pages → {len(texts)} chunks"
        )
        return texts, metadatas

    def save_uploaded_file(self, file_bytes: bytes, filename: str) -> str:
        """Save uploaded PDF bytes to disk and return the full path."""
        safe_name = filename.replace(" ", "_")
        file_path = os.path.join(PDF_UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"Saved uploaded PDF to: {file_path}")
        return file_path
