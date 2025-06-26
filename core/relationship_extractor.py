import re
from typing import Dict, List

class RelationshipExtractor:
    """Extracts relationships from document/code content using pattern matching."""
    
    def __init__(self):
        # Define regex patterns for each relationship type
        self.patterns = {
            "requires": [
                r"use\s+MW_Properties[\\\w]*",  # PHP namespace imports
                r"@requires\s+(WordPress\s+\d+\.\d+\+)",  # Docblock requirements
                r"require.*['\"]MW_Properties",  # JS/PHP requires
                r"include.*['\"]MW_Properties"   # PHP includes
            ],
            "integrates_with": [
                r"add_action\(['\"]mw_properties_\w+['\"]",  # WordPress hooks
                r"add_filter\(['\"]mw_properties_\w+['\"]",
                r"do_action\(['\"]mw_properties_\w+['\"]",
                r"apply_filters\(['\"]mw_properties_\w+['\"]"
            ],
            "extends": [
                r"extends\s+WP_\w+",  # Class extensions
                r"implements\s+\w+_Interface"  # Interface implementations
            ],
            "related_to": [
                r"@see\s+(\w+(?:\\\w+)*)",  # Docblock references
                r"see\s+also:\s+(\w+)"  # Documentation references
            ],
            "prerequisites": [
                r"before\s+using\s+this.*,\s+(?:understand|install|configure)\s+([^\.]+)",
                r"prerequisites?:\s+(.*)"
            ]
        }

    def extract_relationships(self, content: str) -> Dict[str, List[str]]:
        """Extract relationships from document/code content.
        
        Args:
            content: The text content to analyze
            
        Returns:
            Dictionary mapping relationship types to lists of matches
        """
        relationships = {
            "requires": [],
            "integrates_with": [],
            "extends": [],
            "related_to": [],
            "prerequisites": []
        }

        for rel_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Flatten any capture groups and deduplicate
                    cleaned_matches = set()
                    for match in matches:
                        if isinstance(match, tuple):
                            cleaned_matches.update(m for m in match if m)
                        elif match:
                            cleaned_matches.add(match)
                    
                    relationships[rel_type].extend(cleaned_matches)

        # Remove empty relationship types
        return {k: list(set(v)) for k, v in relationships.items() if v}