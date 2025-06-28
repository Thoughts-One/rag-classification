import argparse
import asyncio
import os
import json # Import json
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

from core.classifier import DocumentClassifier
from utils.text_processing import preprocess_text

def classify_single_file(file_path: str, role: Optional[str] = None) -> Dict:
    """Classify a single document from a file path."""
    try:
        path_obj = Path(file_path)
        original_filename = path_obj.name
        
        # Determine if the file is a JSON and load content accordingly
        if path_obj.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                original_file_content = json.load(f)
            content_for_classification = original_file_content.get("content", "")
            source_for_classification = original_file_content.get("source", str(path_obj.parent))
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content_for_classification = f.read()
            original_file_content = {"content": content_for_classification} # Store raw content as a dict
            source_for_classification = str(path_obj.parent)

        document = {
            "content": content_for_classification,
            "source": source_for_classification,
            "filename": original_filename,
            "original_document_content": original_file_content # Pass the original content (parsed JSON or raw text in dict)
        }
        
        classifier = DocumentClassifier()
        result = asyncio.run(classifier.classify_document(document, role))
        return result
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}. Attempting to classify as plain text.")
        with open(file_path, 'r', encoding='utf-8') as f:
            content_for_classification = f.read()
        original_file_content = {"content": content_for_classification}
        path_obj = Path(file_path)
        original_filename = path_obj.name
        source_for_classification = str(path_obj.parent)
        document = {
            "content": content_for_classification,
            "source": source_for_classification,
            "filename": original_filename,
            "original_document_content": original_file_content
        }
        classifier = DocumentClassifier()
        result = asyncio.run(classifier.classify_document(document, role))
        return result
    except Exception as e:
        print(f"Error classifying file {file_path}: {e}")
        return {}

def classify_batch_directory(directory_path: str, role: Optional[str] = None, recursive: bool = False) -> Dict[str, Dict]:
    """Classify all documents in a given directory."""
    results = {}
    for root, dirs, files in os.walk(directory_path):
        if not recursive and root != directory_path:
            # If not recursive, only process the top-level directory
            del dirs[:] # Don't recurse into subdirectories
        for file_name in files:
            file_path = Path(root) / file_name
            if file_path.is_file() and not file_name.startswith('.'): # Skip hidden files
                print(f"Classifying {file_path}...")
                # classify_single_file already handles extracting filename and source from file_path
                result = classify_single_file(str(file_path), role)
                results[str(file_path)] = result
    return results

def main():
    load_dotenv() # Load environment variables from .env file
    parser = argparse.ArgumentParser(description="RAG Classification CLI Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file",
        type=str,
        help="Path to a single file for classification."
    )
    group.add_argument(
        "--directory",
        type=str,
        help="Path to a directory for batch processing."
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process directories recursively. Only applicable with --directory."
    )
    parser.add_argument(
        "--role",
        type=str,
        default=None,
        help="Optional role for classification (e.g., 'legal', 'medical')."
    )

    args = parser.parse_args()

    if args.file:
        file_path = Path(args.file)
        if not file_path.is_file():
            print(f"Error: {args.file} is not a valid file. Please provide a valid file path.")
            return
        print(f"Classifying single file: {args.file}")
        result = classify_single_file(args.file, args.role)
        print("\n--- Single File Classification Result ---")
        print(f"Classification: {result.get('classification', 'N/A')}")
        print(f"Relationships: {result.get('relationships', 'N/A')}")
    elif args.directory:
        directory_path = Path(args.directory)
        if not directory_path.is_dir():
            print(f"Error: {args.directory} is not a valid directory. Please provide a valid directory path.")
            return
        print(f"Starting batch classification for directory: {args.directory} (Recursive: {args.recursive})")
        results = classify_batch_directory(args.directory, args.role, args.recursive)
        print("\n--- Batch Classification Results ---")
        for file_path, result in results.items():
            print(f"File: {file_path}")
            print(f"  Classification: {result.get('classification', 'N/A')}")
            print(f"  Relationships: {result.get('relationships', 'N/A')}")
            print("-" * 30)

if __name__ == "__main__":
    main()