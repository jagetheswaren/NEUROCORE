import os
import shutil
import tempfile
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from server.api.dependencies import get_orchestrator

logger = logging.getLogger("server.routes.knowledge")

router = APIRouter(prefix="/knowledge", tags=["Knowledge (RAG)"])

class TextIngestRequest(BaseModel):
    text: str
    filename: Optional[str] = "raw_input.txt"
    doc_id: Optional[str] = None

class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 3

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    orchestrator=Depends(get_orchestrator)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    # Save to temp file
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        res = orchestrator.knowledge.ingest_file(tmp_path, doc_id=None)
        res["filename"] = file.filename
        return {
            "status": "success",
            "message": f"Successfully indexed '{file.filename}'",
            "details": res
        }
    except Exception as e:
        logger.error(f"Failed to ingest file '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/ingest-text")
def ingest_text(
    req: TextIngestRequest,
    orchestrator=Depends(get_orchestrator)
):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")

    try:
        res = orchestrator.knowledge.ingest_text(req.text, filename=req.filename, doc_id=req.doc_id)
        return {
            "status": "success",
            "message": "Text ingested successfully",
            "details": res
        }
    except Exception as e:
        logger.error(f"Text ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Text ingestion error: {str(e)}")

@router.post("/search")
def search_knowledge(
    req: SearchQuery,
    orchestrator=Depends(get_orchestrator)
):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    try:
        results = orchestrator.knowledge.search(req.query, top_k=req.top_k)
        return {
            "query": req.query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/documents")
def list_documents(orchestrator=Depends(get_orchestrator)):
    try:
        docs = orchestrator.knowledge.list_documents()
        return {
            "count": len(docs),
            "documents": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: str,
    orchestrator=Depends(get_orchestrator)
):
    try:
        success = orchestrator.knowledge.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
        return {
            "status": "success",
            "message": f"Document '{doc_id}' removed from knowledge base."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion error: {str(e)}")
