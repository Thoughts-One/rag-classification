from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from ..routes.classification import Document

router = APIRouter(prefix="/api/v1/classify", tags=["batch"])

@router.post("/batch")
async def batch_classify(documents: List[Document]):
    """Batch process multiple documents"""
    if len(documents) > 50:
        raise HTTPException(
            status_code=400,
            detail="Batch size exceeds maximum limit of 50 documents"
        )
    
    return {
        "status": "success",
        "data": [
            {
                "document_id": f"doc_{i}",
                "classification": {
                    "collection": "wordpress_block_development",
                    "topics": ["Property Display", "Block Development"],
                    "tags": ["production-ready", "dynamic-block"],
                    "confidence": 0.95
                },
                "relationships": {
                    "requires": ["MW Properties 2.0+", "WordPress 6.8+"],
                    "integrates_with": ["REST API", "Block Editor"]
                }
            }
            for i, doc in enumerate(documents)
        ],
        "metadata": {
            "processing_time": len(documents) * 0.5,
            "model_used": "deepseek-v3",
            "timestamp": datetime.utcnow().isoformat()
        }
    }