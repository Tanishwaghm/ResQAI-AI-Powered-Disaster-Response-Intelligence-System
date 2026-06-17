"""
ResQAI - Agent Router (Coordinator Agent)
Automatically routes queries to the most appropriate specialist agent.
Uses keyword matching + LLM-based routing for accuracy.
"""

import logging
from typing import Tuple, Dict

from agents import medical_agent, rescue_agent, navigation_agent, communication_agent
from services.groq_service import GroqService

logger = logging.getLogger(__name__)

AGENTS: Dict[str, object] = {
    "medical": medical_agent,
    "rescue": rescue_agent,
    "navigation": navigation_agent,
    "communication": communication_agent,
}

AGENT_DESCRIPTIONS = {
    "medical": "First aid, injuries, CPR, medical emergencies, health conditions",
    "rescue": "Evacuation, shelter, escape from buildings, disaster rescue procedures",
    "navigation": "Safe routes, roads to avoid, movement during disaster, directions",
    "communication": "Emergency contact numbers, helplines, alerts, who to call",
}

ROUTER_SYSTEM_PROMPT = """You are an emergency query router. Your job is to decide which specialist agent
should handle a given emergency query.

Available agents:
- medical: First aid, injuries, CPR, medical emergencies
- rescue: Evacuation, shelter, building escape, rescue procedures  
- navigation: Safe routes, roads to avoid, movement guidance
- communication: Emergency contacts, helplines, alert systems

Respond with ONLY the agent name in lowercase: medical, rescue, navigation, or communication."""


class AgentRouter:
    """
    Coordinator Agent — routes incoming queries to the best specialist agent
    and generates a response using that agent's system prompt.
    """

    def __init__(self, groq_service: GroqService):
        self.groq = groq_service

    def _keyword_score(self, query: str) -> Dict[str, int]:
        """Score each agent by keyword overlap with the query."""
        query_lower = query.lower()
        scores = {}
        for name, agent in AGENTS.items():
            keywords = agent.get_keywords()
            score = sum(1 for kw in keywords if kw in query_lower)
            scores[name] = score
        return scores

    def _llm_route(self, query: str) -> str:
        """Use LLM for routing when keyword scores are ambiguous."""
        prompt = f"""Emergency query: "{query}"

Which specialist agent should handle this? Choose one: medical, rescue, navigation, communication"""
        result = self.groq.single_shot(prompt, ROUTER_SYSTEM_PROMPT)
        result = result.strip().lower()
        if result not in AGENTS:
            return "rescue"  # Default fallback
        return result

    def route(self, query: str, force_agent: str = None) -> Tuple[str, str]:
        """
        Determine the best agent for the query.
        Returns (agent_name, explanation).
        """
        if force_agent and force_agent in AGENTS:
            return force_agent, f"Agent manually selected by user: {force_agent}"

        # Keyword scoring first (fast)
        scores = self._keyword_score(query)
        max_score = max(scores.values())

        if max_score >= 2:
            # Clear winner from keywords
            best_agent = max(scores, key=scores.get)
            explanation = (
                f"Routed to {best_agent} agent based on query keywords "
                f"(score: {max_score}). Specializes in: {AGENT_DESCRIPTIONS[best_agent]}"
            )
        else:
            # Ambiguous — use LLM to decide
            best_agent = self._llm_route(query)
            explanation = (
                f"Routed to {best_agent} agent via AI analysis. "
                f"Specializes in: {AGENT_DESCRIPTIONS[best_agent]}"
            )

        logger.info(f"Query routed to: {best_agent} | Scores: {scores}")
        return best_agent, explanation

    def respond(
        self,
        query: str,
        session_id: str = "default",
        force_agent: str = None,
        context: str = "",
    ) -> Tuple[str, str, str]:
        """
        Route the query and generate a response using the selected agent's prompt.
        Returns (answer, agent_name, explanation).
        """
        agent_name, explanation = self.route(query, force_agent)
        agent_module = AGENTS[agent_name]
        system_prompt = agent_module.get_system_prompt()

        # Inject RAG context if available
        if context:
            user_message = f"""Use this verified knowledge base context:

{context}

Query: {query}"""
        else:
            user_message = query

        answer = self.groq.chat(
            user_message=user_message,
            system_prompt=system_prompt,
            session_id=session_id,
        )

        return answer, agent_name, explanation
