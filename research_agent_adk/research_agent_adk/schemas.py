from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    question: str = Field(..., description="User research question about agentic AI for enterprise")
    max_sources: int = Field(5, ge=1, le=10, description="Maximum number of sources to include")


class Source(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source] = []