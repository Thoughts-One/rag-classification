import re
from typing import Optional

def preprocess_text(text: str) -> str:
    """Preprocess text for classification by:
    - Normalizing whitespace
    - Removing code blocks
    - Removing special characters
    - Trimming to reasonable length
    """
    if not text:
        return ""
    
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,;:!?\-]', '', text)
    
    # Trim to first 10k characters to avoid excessive API costs
    return text[:10000]

def extract_code_blocks(text: str) -> list[str]:
    """Extract all code blocks from text"""
    return re.findall(r'```(?:[a-z]+\n)?(.*?)```', text, flags=re.DOTALL)

def extract_imports(code: str) -> list[str]:
    """Extract import statements from code"""
    imports = re.findall(r'^\s*(?:from\s+(\w+)|import\s+([\w\s,]+))', code, flags=re.MULTILINE)
    return [imp[0] or imp[1] for imp in imports if any(imp)]