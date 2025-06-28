from typing import Dict, Optional
from models.llm_client import LLMClient
from storage.classification_cache import ClassificationCache
from storage.relationship_store import RelationshipStore
from storage.file_saver import FileSaver # Import FileSaver
from utils.text_processing import preprocess_text
from pathlib import Path
import yaml

TAXONOMY = yaml.safe_load((Path(__file__).parent.parent / "config" / "taxonomy.yaml").read_text())

class DocumentClassifier:
    def __init__(self):
        self.llm_client = LLMClient()
        self.cache = ClassificationCache()
        self.relationship_store = RelationshipStore()
        self.file_saver = FileSaver() # Initialize FileSaver

    async def classify_document(self, document: Dict, role: Optional[str] = None) -> Dict:
        """
        Classify a document with optional role-specific processing and save the result.

        Args:
            document (Dict): The document to classify, expected to contain 'content',
                             'source' (original path), and 'filename' (original filename).
            role (Optional[str]): The optional role for classification.

        Returns:
            Dict: The classification result.
        """
        original_content = document.get("content", "")
        original_source_path = document.get("source", "unknown_path")
        original_filename = document.get("filename", "unknown_file")

        # Check cache first
        cache_key = self._generate_cache_key(document)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            # If cached, ensure it has the necessary structure for saving
            if "classification" in cached_result and "relationships" in cached_result:
                # Simulate processing time for cached results if needed for metadata
                cached_result["processing_time_seconds"] = 0.0 # Or retrieve from cache metadata
                self.file_saver.save_classified_document(
                    original_document_data=document, # Pass the entire document dict
                    classification_result=cached_result,
                    original_filename=original_filename
                )
            return cached_result

        # Preprocess text
        processed_content = preprocess_text(original_content)

        # Start timing for classification
        import time
        start_time = time.time()

        # Get classification from LLM
        classification = await self.llm_client.classify(
            content=processed_content,
            role=role
        )

        # Extract relationships
        relationships = self._extract_relationships(document)

        end_time = time.time()
        processing_time = end_time - start_time

        # Store results
        result = {
            "classification": classification,
            "relationships": relationships,
            "processing_time_seconds": processing_time # Add processing time to result
        }
        self.cache.set(cache_key, result)
        if document.get("id"):
            self.relationship_store.store(str(document["id"]), relationships)

        # Save the classified document to file
        self.file_saver.save_classified_document(
            original_document_data=document, # Pass the entire document dict
            classification_result=result,
            original_filename=original_filename
        )

        return result

    def _generate_cache_key(self, document: Dict) -> str:
        """Generate a unique cache key for the document"""
        content_hash = hash(document.get("content", ""))
        return f"{document.get('source', '')}_{content_hash}"

    def _extract_relationships(self, document: Dict) -> Dict:
        """Extract relationships from document content using RelationshipExtractor"""
        from core.relationship_extractor import RelationshipExtractor
        extractor = RelationshipExtractor()
        content = document.get("content", "")
        return extractor.extract_relationships(content)