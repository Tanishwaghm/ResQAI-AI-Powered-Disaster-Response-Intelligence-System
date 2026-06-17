"""
ResQAI - Groq LLM Service
Handles all LLM calls through Groq's API using Llama 3.3 70B.
"""

import logging
from typing import List, Dict, Optional

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE

logger = logging.getLogger(__name__)

# In-memory conversation history keyed by session_id
_memory: Dict[str, List[Dict[str, str]]] = {}


class GroqService:
    """
    Wraps the Groq client for chat completions with multi-turn memory support.
    """

    def __init__(self):
        if not GROQ_API_KEY:
            raise EnvironmentError("GROQ_API_KEY is not set in environment variables.")
        self.client = Groq(api_key=GROQ_API_KEY)
        logger.info(f"GroqService initialized with model: {GROQ_MODEL}")

    def chat(
        self,
        user_message: str,
        system_prompt: str,
        session_id: str = "default",
        max_history: int = 10,
    ) -> str:
        """
        Send a message to the LLM with conversation memory.
        Returns the assistant's response as a string.
        """
        # Initialize session memory if needed
        if session_id not in _memory:
            _memory[session_id] = []

        history = _memory[session_id]

        # Append user message to history
        history.append({"role": "user", "content": user_message})

        # Trim history to max_history turns (keep last N pairs)
        if len(history) > max_history * 2:
            history = history[-(max_history * 2):]
            _memory[session_id] = history

        messages = [{"role": "system", "content": system_prompt}] + history

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=GROQ_MAX_TOKENS,
                temperature=GROQ_TEMPERATURE,
            )
            assistant_reply = response.choices[0].message.content.strip()

            # Save assistant reply to history
            _memory[session_id].append(
                {"role": "assistant", "content": assistant_reply}
            )

            return assistant_reply

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise RuntimeError(f"LLM call failed: {e}")

    def single_shot(self, prompt: str, system_prompt: str = "") -> str:
        """
        One-off LLM call without memory (used for classification tasks).
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=100,
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq single_shot error: {e}")
            return "OTHER"

    def clear_session(self, session_id: str) -> None:
        """Clear conversation memory for a session."""
        if session_id in _memory:
            del _memory[session_id]

    def health_check(self) -> str:
        try:
            self.single_shot("Say OK", "You are a health check.")
            return "OK"
        except Exception as e:
            return f"ERROR: {e}"
