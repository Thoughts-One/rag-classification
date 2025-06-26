from typing import Dict, Optional
from ..models.llm_client import LLMClient
from ..storage.classification_cache import ClassificationCache
from ..storage.relationship_store import RelationshipStore
from ..utils.text_processing import preprocess_text
from ..config.taxonomy import TAXONOMY

class DocumentClassifier:
    def __init__(self):
        self.llm_client = LLMClient()
        self.cache = ClassificationCache()
        self.relationship_store = RelationshipStore()

    async def classify_document(self, document: Dict, role: Optional[str] = None):
        """Classify a document with optional role-specific processing"""
        # Check cache first
        cache_key = self._generate_cache_key(document)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        # Preprocess text
        processed_content = preprocess_text(document.get("content", ""))

        # Get classification from LLM
        classification = await self.llm_client.classify(
            content=processed_content,
            role=role
        )

        # Extract relationships
        relationships = self._extract_relationships(document)

        # Store results
        result = {
            "classification": classification,
            "relationships": relationships
        }
        self.cache.set(cache_key, result)
        if document.get("id"):
            self.relationship_store.store(str(document["id"]), relationships)

        return result

    def _generate_cache_key(self, document: Dict) -> str:
        """Generate a unique cache key for the document"""
        content_hash = hash(document.get("content", ""))
        return f"{document.get('source', '')}_{content_hash}"

    def _extract_relationships(self, document: Dict) -> Dict:
        """Extract relationships from document content"""
        # Placeholder - will be implemented in relationship_extractor.py
        return {
            "requires": [],
            "integrates_with": [],
            "related_to": []
        }