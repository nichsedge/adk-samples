from typing import List, Dict, Any
from google.adk.tools import google_search  # Built-in ADK search tool


def summarize_sources_tool(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simple deterministic summarizer tool placeholder.
    In practice, you would let the LLM summarize; here we provide a tool the agent can call
    to transform raw search results into a compact bullet summary with titles and URLs.

    Args:
        results: A list of dicts returned from google_search (title, url, snippet, etc.)

    Returns:
        dict with keys:
          status: "success"
          bullets: list[str] - compact summary bullet points
          sources: list[dict] - pass-through of top sources with title/url/snippet
    """
    bullets: List[str] = []
    sources: List[Dict[str, Any]] = []
    for r in results[:5]:
        title = r.get("title") or "Untitled"
        url = r.get("url") or r.get("link") or ""
        snippet = r.get("snippet") or r.get("description") or ""
        bullets.append(f"- {title}: {snippet[:180]}".strip())
        sources.append({"title": title, "url": url, "snippet": snippet})

    return {"status": "success", "bullets": bullets, "sources": sources}


# Expose tools in a list for convenience
ALL_TOOLS = [google_search, summarize_sources_tool]