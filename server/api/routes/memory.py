from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from server.api.dependencies import get_orchestrator

router = APIRouter(prefix="/memory", tags=["Memory"])

class MemoryItem(BaseModel):
    content: str
    category: Optional[str] = "general"

class SearchQuery(BaseModel):
    query: str

@router.get("")
def list_memories(orchestrator=Depends(get_orchestrator)):
    try:
        memories = orchestrator.memory_db.get_all()
        return {
            "count": len(memories),
            "memories": [{"id": m[0], "content": m[1], "category": m[2], "created_at": m[3]} for m in memories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("")
def add_memory(item: MemoryItem, orchestrator=Depends(get_orchestrator)):
    if not item.content or not item.content.strip():
        raise HTTPException(status_code=400, detail="Memory content cannot be empty.")

    try:
        msg = orchestrator.remember(item.content)
        return {"status": "success", "message": msg, "saved_content": item.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save memory: {e}")

@router.post("/search")
def search_memories(q: SearchQuery, orchestrator=Depends(get_orchestrator)):
    try:
        all_mem = orchestrator.memory_db.get_all()
        results = orchestrator.retrieve_memories(all_mem, q.query)
        return {
            "query": q.query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")
