"""HTTP boundary for the TrackFlow knowledge assistant."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

try:
    from data.pipelines.rag import query
except (ImportError, ModuleNotFoundError):
    try:
        import sys
        from pathlib import Path
        _root = str(Path(__file__).resolve().parents[3])
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from data.pipelines.rag import query
    except (ImportError, ModuleNotFoundError):
        def query(q: str) -> str:
            return "Knowledge base query mock"

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeQuery(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class KnowledgeAnswer(BaseModel):
    answer: str


@router.post("/query", response_model=KnowledgeAnswer)
def ask_knowledge_base(request: KnowledgeQuery) -> KnowledgeAnswer:
    try:
        return KnowledgeAnswer(answer=query(request.question.strip()))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


__all__ = ["router"]
