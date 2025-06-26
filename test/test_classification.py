import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.classifier import DocumentClassifier
from core.error_handling import ClassificationError

class TestDocumentClassifier:
    """Test suite for DocumentClassifier functionality"""
    
    @pytest.fixture
    def classifier(self):
        """Fixture providing a configured DocumentClassifier instance"""
        return DocumentClassifier()
    
    @pytest.mark.asyncio
    async def test_basic_classification(self, classifier):
        """Test basic document classification"""
        document = {
            "content": "Sample WordPress block registration code",
            "title": "Test Block",
            "source": "wordpress_blocks"
        }
        
        result = await classifier.classify_document(document)
        
        assert "collection" in result
        assert "topics" in result
        assert "tags" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], float)
        
    @pytest.mark.asyncio
    async def test_empty_document(self, classifier):
        """Test classification with empty document content"""
        with pytest.raises(ClassificationError):
            await classifier.classify_document({
                "content": "",
                "title": "Empty Document"
            })
            
    @pytest.mark.asyncio
    async def test_missing_fields(self, classifier):
        """Test classification with missing required fields"""
        with pytest.raises(ClassificationError):
            await classifier.classify_document({
                "title": "Missing Content Field"
            })

    @pytest.mark.asyncio
    async def test_wordpress_block_classification(self, classifier):
        """Test WordPress block-specific classification"""
        document = {
            "content": "function register_property_block() { wp_register_block_type(...) }",
            "title": "Property Block Registration",
            "source": "wordpress_blocks"
        }
        
        result = await classifier.classify_document(document)
        
        assert result["collection"] == "wordpress_block_development"
        assert "dynamic-block" in result["tags"]
        assert result["confidence"] > 0.8

if __name__ == "__main__":
    pytest.main()