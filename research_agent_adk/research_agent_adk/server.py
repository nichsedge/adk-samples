import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from .config import Settings
from .agent import build_research_agent
from .schemas import QueryRequest, QueryResponse, Source


app = FastAPI(title="Research Agent ADK", version="0.1.0", docs_url="/docs", openapi_url="/openapi.json")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    try:
        settings = Settings.from_env()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    agent = build_research_agent(settings.model_id)

    # Prepare session and runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="research_agent_adk",
        user_id="service",
        session_id="service-session",
    )
    runner = Runner(agent=agent, app_name="research_agent_adk", session_service=session_service)

    # Prepare user content
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=req.question)])

    # Run agent async and collect final answer; optionally capture intermediate tool events
    final_answer: str | None = None
    collected_sources: list[Source] = []

    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=content
    ):
        # When the agent yields its final response:
        if event.is_final_response():
            try:
                final_answer = event.content.parts[0].text or ""
            except Exception:
                final_answer = ""

        # If tool results include structured sources, you could parse them here.
        # Leaving as a placeholder to keep service minimal.
        # Example pseudo:
        # if event.is_function_response():
        #     if event.name == "google_search":
        #         # parse results if present and map to Source(...)
        #         pass

    if not final_answer:
        raise HTTPException(status_code=502, detail="No final response from agent")

    # The agent is instructed to cite and synthesize. We also return empty sources list here,
    # but your tool can be extended to surface sources via function responses if desired.
    return JSONResponse(
        status_code=200,
        content=QueryResponse(answer=final_answer, sources=collected_sources).model_dump(),
    )


def main():
    # Entry point for console_script if needed locally (not used by uvicorn when run as module)
    import uvicorn
    try:
        settings = Settings.from_env()
    except ValueError:
        # Fall back to defaults for local dev when env missing
        class _S:
            port = 8080
        settings = _S()  # type: ignore[assignment]
    uvicorn.run("research_agent_adk.server:app", host="0.0.0.0", port=getattr(settings, "port", 8080), reload=False)


if __name__ == "__main__":
    # Allow `python -m research_agent_adk.server`
    main()