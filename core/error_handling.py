from enum import Enum
from typing import Dict, Optional
import logging
from datetime import datetime

class ClassificationError(Exception):
    """Base exception for classification errors"""
    pass

class LLMServiceError(ClassificationError):
    """LLM service unavailable or failed"""
    pass

class ValidationError(ClassificationError):
    """Input validation failed"""
    pass

class ConfidenceError(ClassificationError):
    """Classification confidence too low"""
    pass

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fallback_strategies = {
            LLMServiceError: self._handle_llm_service_error,
            ValidationError: self._handle_validation_error,
            ConfidenceError: self._handle_confidence_error
        }
    
    async def handle_error(self, error: Exception, context: Dict) -> Optional[Dict]:
        """Handle classification errors with appropriate fallback strategies"""
        error_type = type(error)
        severity = self._determine_severity(error)
        
        self.logger.error(
            f"Classification error: {error_type.__name__}: {str(error)}",
            extra={"context": context, "severity": severity.value}
        )
        
        if error_type in self.fallback_strategies:
            return await self.fallback_strategies[error_type](error, context)
        
        # Generic fallback
        return await self._generic_fallback(error, context)
    
    async def _handle_llm_service_error(self, error: LLMServiceError, context: Dict) -> Optional[Dict]:
        """Handle LLM service failures"""
        # Try fallback model
        try:
            from models.llm_client import LLMClient
            fallback_client = LLMClient()
            return await fallback_client.classify(context["document"].get("content", ""), role="CODE")
        except Exception as fallback_error:
            self.logger.error(f"Fallback model also failed: {fallback_error}")
            return await self._rule_based_fallback(context)
    
    async def _handle_validation_error(self, error: ValidationError, context: Dict) -> Optional[Dict]:
        """Handle input validation errors"""
        # Attempt to clean and retry
        cleaned_document = self._clean_document(context["document"])
        if cleaned_document:
            try:
                from core.classifier import DocumentClassifier
                classifier = DocumentClassifier()
                return await classifier.classify_document(cleaned_document)
            except Exception:
                pass
        
        return None  # Cannot recover from validation errors
    
    async def _handle_confidence_error(self, error: ConfidenceError, context: Dict) -> Optional[Dict]:
        """Handle low confidence classifications"""
        # Try with a more powerful model
        try:
            from models.llm_client import LLMClient
            premium_client = LLMClient()
            return await premium_client.classify(context["document"].get("content", ""), role="CODE")
        except Exception:
            # Return low-confidence result with warning
            result = context.get("partial_result", {})
            result["confidence_warning"] = True
            result["confidence"] = max(result.get("confidence", 0.0), 0.3)  # Minimum confidence
            return result
    
    async def _generic_fallback(self, error: Exception, context: Dict) -> Dict:
        """Generic fallback when no specific handler exists"""
        return await self._rule_based_fallback(context)
    
    async def _rule_based_fallback(self, context: Dict) -> Dict:
        """Simple rule-based classification when LLMs fail"""
        document = context["document"]
        content = document.get("content", "").lower()
        title = document.get("title", "").lower()
        
        # Simple keyword-based classification
        if any(keyword in content or keyword in title for keyword in ["block", "gutenberg", "wp_register_block"]):
            return {
                "collection": "wordpress_block_development",
                "topics": ["Block Development", "General", "Unknown", "Fallback"],
                "tags": ["fallback-classification", "requires-review"],
                "confidence": 0.3,
                "model_used": "rule-based-fallback",
                "relationships": {}
            }
        elif any(keyword in content or keyword in title for keyword in ["theme", "template", "fse"]):
            return {
                "collection": "wordpress_theme_development",
                "topics": ["Theme Development", "General", "Unknown", "Fallback"],
                "tags": ["fallback-classification", "requires-review"],
                "confidence": 0.3,
                "model_used": "rule-based-fallback",
                "relationships": {}
            }
        else:
            return {
                "collection": "general_documentation",
                "topics": ["General", "Unknown", "Fallback", "Unclassified"],
                "tags": ["fallback-classification", "requires-review", "manual-classification-needed"],
                "confidence": 0.1,
                "model_used": "rule-based-fallback",
                "relationships": {}
            }
    
    def _clean_document(self, document: Dict) -> Optional[Dict]:
        """Attempt to clean malformed document data"""
        try:
            cleaned = {
                "content": str(document.get("content", ""))[:10000],  # Truncate long content
                "title": str(document.get("title", ""))[:200],  # Truncate long titles
                "source": str(document.get("source", "unknown")),
                "metadata": document.get("metadata", {})
            }
            
            # Ensure minimum content length
            if len(cleaned["content"]) < 10:
                return None
            
            return cleaned
        except Exception:
            return None
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity for monitoring and alerting"""
        if isinstance(error, ValidationError):
            return ErrorSeverity.LOW
        elif isinstance(error, ConfidenceError):
            return ErrorSeverity.MEDIUM
        elif isinstance(error, LLMServiceError):
            return ErrorSeverity.HIGH
        else:
            return ErrorSeverity.CRITICAL