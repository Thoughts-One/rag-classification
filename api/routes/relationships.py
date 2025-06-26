from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from storage.relationship_store import RelationshipStore

router = APIRouter(prefix="/api/v1/relationships", tags=["relationships"])
relationship_store = RelationshipStore()

@router.get("/{document_id}")
async def get_relationships(document_id: str):
    """Retrieve relationship metadata for a document"""
    try:
        relationships = relationship_store.get_relationships(document_id)
        return {
            "status": "success",
            "data": {
                "document_id": document_id,
                "relationships": relationships
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get relationships: {str(e)}"
        )

@router.get("/dependencies/{document_id}")
async def get_dependencies(document_id: str):
    """Get dependency chain for a document"""
    try:
        relationships = relationship_store.get_relationships(document_id)
        return {
            "status": "success",
            "data": {
                "document_id": document_id,
                "dependencies": relationships.get("requires", [])
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dependencies: {str(e)}"
        )

@router.post("/query")
async def query_relationships(filters: dict):
    """Query relationships by criteria"""
    try:
        results = relationship_store.query_relationships(filters)
        return {
            "status": "success",
            "data": {
                "matches": results
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )