import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class FileSaver:
    def __init__(self):
        load_dotenv()
        self.data_dir = os.getenv("DATA_DIR")
        if not self.data_dir:
            raise ValueError("DATA_DIR environment variable not set.")
        self.base_path = Path(self.data_dir)

    def save_classified_document(self, original_document_data: Dict, classification_result: Dict, original_filename: str):
        """
        Saves a classified document to the specified directory structure.

        Args:
            original_document_data (Dict): The original document content and metadata,
                                           which might be a parsed JSON object or raw content in a dict.
            classification_result (Dict): The classification results, including refined_source.
            original_filename (str): The original filename of the document.
        """
        # Use the 'source' from the original document data for directory creation
        source_for_directory = original_document_data.get("source", "unknown_source")
        
        # Sanitize source to create a valid directory name
        sanitized_source = "".join(c for c in source_for_directory if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        sanitized_source = sanitized_source.replace(" ", "_")

        target_directory = self.base_path / sanitized_source
        target_directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use original filename, but ensure it's valid and append .json
        safe_filename = "".join(c for c in original_filename if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_filename:
            safe_filename = "untitled"
        
        # Remove existing extension and add .json
        safe_filename_stem = Path(safe_filename).stem
        output_filename = f"{safe_filename_stem}_{timestamp}.json"
        output_path = target_directory / output_filename

        # Determine the content to save for "original_document"
        # If original_document_data.get("original_document_content") is a dict (parsed JSON), save it as a dict.
        # Otherwise, assume it's raw content and save it as a string under a "content" key.
        original_content_to_save = original_document_data.get("original_document_content", {})
        if not isinstance(original_content_to_save, dict):
            original_content_to_save = {"content": original_content_to_save} # Wrap raw content in a dict

        # Prepare the enhanced JSON structure
        enhanced_data = {
            "original_document": original_content_to_save, # Use the correctly formatted original content
            "original_metadata": {
                "source_path": original_document_data.get("source", "N/A"),
                "original_filename": original_filename,
                "timestamp_processed": datetime.now().isoformat()
            },
            "classification_results": classification_result.get("classification", {}),
            "relationships": classification_result.get("relationships", {}),
            "processing_metadata": {
                "model_used": classification_result.get("classification", {}).get("model_used", "N/A"),
                "confidence": classification_result.get("classification", {}).get("confidence", "N/A"),
                "processing_time_seconds": classification_result.get("processing_time_seconds", "N/A")
            }
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, indent=4)
            print(f"Successfully saved classified document to: {output_path}")
        except IOError as e:
            print(f"Error saving file {output_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving file {output_path}: {e}")
