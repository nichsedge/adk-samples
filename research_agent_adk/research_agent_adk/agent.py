from typing import List, Dict, Any
from google.adk.agents import Agent
from .tools import ALL_TOOLS


def build_research_agent(model_id: str) -> Agent:
    """
    Create an ADK Agent configured for researching 'Agentic AI for Enterprise'.
    Uses Gemini 2.0 Pro and tools: google_search + summarize_sources_tool.
    """
    instruction = (
        "You are an enterprise research assistant specialized in Agentic AI, "
        "covering architectures, evaluation, compliance, governance, risk, "
        "cost, integration patterns, and real-world adoption in large organizations. "
        "Research the web using tools when needed. Prioritize credible sources "
        "(peer-reviewed papers, vendor docs, reputable blogs, and analyst reports). "
        "Always provide a concise synthesis and list sources. "
        "Prefer bullet points for findings. Avoid hallucinations; if uncertain, say so."
    )

    description = (
        "Enterprise research assistant focused on agentic AI: patterns, "
        "trade-offs, enterprise integration, evaluation, and governance."
    )

    agent = Agent(
        name="enterprise_agentic_ai_researcher",
        model=model_id,
        instruction=instruction,
        description=description,
        tools=ALL_TOOLS,
    )
    return agent