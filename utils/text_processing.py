import re
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

def preprocess_text(text: str) -> str:
    """Preprocess text for classification by:
    - Normalizing whitespace
    - Removing HTML tags
    - Removing code blocks
    - Removing special characters
    - Trimming to reasonable length
    """
    if not text:
        return ""
    
    # Convert HTML lists to markdown lists
    text = re.sub(r'<ul>', '', text)
    text = re.sub(r'</ul>', '', text)
    text = re.sub(r'<li>(.*?)</li>', r'- \1\n', text)

    # Preserve link text, remove tags
    text = re.sub(r'<a[^>]*?>(.*?)</a>', r'\1', text)

    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,;:!?\-]', '', text)
    
    # Trim to first 10k characters to avoid excessive API costs
    return text[:10000]

def extract_code_blocks(text: str) -> List[str]:
    """Extract all code blocks from text"""
    return re.findall(r'```(?:[a-z]+\n)?(.*?)```', text, flags=re.DOTALL)

def extract_imports(code: str) -> List[str]:
    """Extract import statements from code"""
    imports = re.findall(r'^\s*(?:from\s+(\w+)|import\s+([\w\s,]+))', code, flags=re.MULTILINE)
    return [imp[0] or imp[1] for imp in imports if any(imp)]

def validate_document(doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate document structure and add missing fields with defaults"""
    if not isinstance(doc, dict):
        logging.debug(f"Document is not a dictionary: {type(doc)}")
        return None
    
    required_fields = {
        'content': '',
        'title': 'Untitled',
        'source': 'unknown',
        'url': ''
    }
    
    # Validate required fields
    validated = {}
    for field, default in required_fields.items():
        if field not in doc or not doc[field]:
            if field == 'content' and field not in doc:
                logging.warning(f"Missing required field: {field}")
                return None
            validated[field] = doc.get(field, default)
            if field != 'content':
                logging.debug(f"Added default value for missing field: {field}")
        else:
            validated[field] = doc[field]
    
    # Add metadata if missing
    validated['metadata'] = doc.get('metadata', {})
    return validated

def process_json_file(filepath: str) -> List[Dict[str, Any]]:
    """Process a single JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            items = json.load(f)
            if isinstance(items, list):
                return items
            else:
                return [items]
    except Exception as e:
        logging.error(f"Error loading {filepath}: {str(e)}")
        return []

def process_markdown_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Process a single Markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Placeholder for future metadata extraction
        filename = os.path.basename(filepath)
        chapter_info = {} # Will be implemented later
        title = filename # Will be implemented later
        source_type = 'markdown_document' # Will be implemented later
        
        return {
            'source': source_type,
            'title': title,
            'content': content,
            'url': f'file://{os.path.abspath(filepath)}',
            'timestamp': datetime.now().isoformat(),
            'format': 'markdown',
            'chapter_info': chapter_info
        }
    except Exception as e:
        logging.error(f"Error processing {filepath}: {str(e)}")
        return None