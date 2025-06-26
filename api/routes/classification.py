from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ...core.classifier import DocumentClassifier

router = APIRouter(prefix="/api/v1/classify", tags=["classification"])
classifier = DocumentClassifier()

class Document(BaseModel):
    content: str
    title: Optional[str] = None
    source: Optional[str] = None
    role: Optional[str] = None
    metadata: Optional[dict] = None
    id: Optional[str] = None

@router.post("/document")
async def classify_document(document: Document):
    """Classify a complete document with relationship extraction"""
    try:
        result = await classifier.classify_document({
            "content": document.content,
            "title": document.title,
            "source": document.source,
            "id": document.id,
            "metadata": document.metadata
        }, role=document.role)

        return {
            "status": "success",
            "data": result,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )

@router.post("/chunk")
async def classify_chunk(document: Document):
    """Classify a document chunk for real-time processing"""
    try:
        result = await classifier.classify_document({
            "content": document.content,
            "title": document.title,
            "source": document.source,
            "id": document.id,
            "metadata": document.metadata
        }, role=document.role)

        return {
            "status": "success",
            "data": result,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )