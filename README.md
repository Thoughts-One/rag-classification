# Project Description: RAG PTRE Website Document Classification

This document provides a comprehensive overview of the RAG PTRE (Retrieval-Augmented Generation for Post-Training Reinforcement Learning) Website Document Classification project. Its primary purpose is to classify WordPress-focused documents and extract relationships for use in RAG systems.
## Project Features

- Document classification with role-specific optimization
- Relationship extraction (dependencies, integrations)
- Code-aware processing for technical documentation
- Multi-model LLM integration with fallback
- Caching and performance optimization

## Prerequisites

- Python 3.9+
- pip package manager

## Setup and Installation

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set required environment variables**: (e.g., in a `.env` file or your shell environment)
    ```bash
    # Get your key from https://openrouter.ai/keys
    export OPENROUTER_API_KEY=your_key_here

    # Optional alternative providers
    # export DEEPSEEK_API_KEY=your_key
    # export OPENAI_API_KEY=your_key
    ```

## Configuration Details

Edit the YAML files in `config/` to customize:
- Classification taxonomy
- Relationship extraction patterns
- Role-specific processing


## 1. Process Flow

The core workflow of this project involves processing input files or directories, classifying their content, extracting relationships, and storing the results in a structured format. The process flow is as follows:

1.  **CLI Argument Parsing**: The application starts by parsing command-line arguments provided by the user via [`cli.py`](cli.py). This includes specifying input files or directories, recursion options, and the role for classification.
2.  **File/Directory Input Processing**: Based on the parsed arguments, the system identifies and processes the input documents. If a directory is provided, it can recursively traverse it to find relevant files.
3.  **DocumentClassifier Orchestration**: The [`DocumentClassifier`](core/classifier.py:class_DocumentClassifier) in [`core/classifier.py`](core/classifier.py) orchestrates the main classification and extraction process:
    *   **Cache Check**: It first checks if the document has already been classified and cached using [`classification_cache.py`](storage/classification_cache.py) to improve performance.
    *   **Preprocessing**: Documents undergo text preprocessing via [`text_processing.py`](utils/text_processing.py) to prepare them for analysis.
    *   **LLM Classification**: The preprocessed content is then sent to a Language Model (LLM) for classification. This interaction is managed through [`llm_client.py`](models/llm_client.py) and specifically implemented by [`openrouter_client.py`](models/openrouter_client.py) for API integration. The classification schema is defined in [`taxonomy.yaml`](config/taxonomy.yaml).
    *   **Relationship Extraction**: After classification, relationships within the document are extracted using [`relationship_extractor.py`](core/relationship_extractor.py). The patterns for extraction are configured in [`relationship_patterns.yaml`](config/relationship_patterns.yaml).
4.  **FileSaver Structured Output**: The classified content, metadata, and extracted relationships are then saved in a structured JSON format using [`file_saver.py`](storage/file_saver.py). Each output includes a timestamp and relevant metadata.
5.  **Results Display**: Finally, the results of the classification and extraction are displayed to the user, typically in the console.

## 2. Main File Connections

The project's architecture is organized into a 5-layer system: CLI, Core, Models, Storage, Utils, and Config. Here's how [`cli.py`](cli.py) connects to individual files and modules to drive the workflow:

*   **[`cli.py`](cli.py)**: This is the main entry point, containing the [`main()`](cli.py:function_main) function. It uses the `invoke` library to define command-line tasks.
    *   It interacts with the `core` module, primarily by instantiating and calling methods on the [`DocumentClassifier`](core/classifier.py:class_DocumentClassifier).
    *   It handles file and directory input, potentially using utilities from `utils/text_processing.py` for initial processing before passing to the classifier.
    *   It directs the output to the `storage` module, specifically to [`file_saver.py`](storage/file_saver.py) for saving results.

*   **`core/`**:
    *   [`classifier.py`](core/classifier.py): Contains the [`DocumentClassifier`](core/classifier.py:class_DocumentClassifier) class, which is the main orchestrator. It imports and utilizes components from `models/`, `storage/`, and `utils/`.
    *   [`relationship_extractor.py`](core/relationship_extractor.py): Used by `classifier.py` to extract relationships based on patterns defined in `config/relationship_patterns.yaml`.
    *   [`error_handling.py`](core/error_handling.py): Provides centralized error management for the core logic.

*   **`models/`**:
    *   [`llm_client.py`](models/llm_client.py): Provides an abstraction layer for interacting with LLMs.
    *   [`openrouter_client.py`](models/openrouter_client.py): Implements the LLM client specifically for the OpenRouter API, used by `classifier.py` via `llm_client.py`.

*   **`storage/`**:
    *   [`file_saver.py`](storage/file_saver.py): Responsible for saving the structured output (JSON) of classified documents. It's called by `cli.py` or `classifier.py`.
    *   [`classification_cache.py`](storage/classification_cache.py): Used by `classifier.py` to manage caching of classification results.
    *   [`relationship_store.py`](storage/relationship_store.py): Likely used by `relationship_extractor.py` or `classifier.py` to store extracted relationships.

*   **`utils/`**:
    *   [`text_processing.py`](utils/text_processing.py): Contains utility functions for text preprocessing, used by `classifier.py`.

*   **`config/`**:
    *   [`taxonomy.yaml`](config/taxonomy.yaml): Defines the WordPress classification schema, loaded by `classifier.py`.
    *   [`relationship_patterns.yaml`](config/relationship_patterns.yaml): Defines patterns for relationship extraction, loaded by `relationship_extractor.py`.

## 3. CLI Commands

The project uses `invoke` for its command-line interface. The main entry point is `cli.py`.

### Basic Usage

To run the CLI, you typically use `python cli.py` followed by the task name.

```bash
python cli.py [options]
```

### Available Commands and Options

## Usage as a Python Library

You can import and use the `DocumentClassifier` directly in your Python applications:

```python
from rag_classification import DocumentClassifier
import asyncio

async def main():
    classifier = DocumentClassifier()
    document = {"content": "This document talks about Python and FastAPI.", "source": "example.txt"}
    result = await classifier.classify_document(document, role="developer")
    print("Classification Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

The `cli.py` script provides command-line access for classifying single files or processing entire directories.

*   **Classify a single file:**
    ```bash
    python cli.py --file your_document.txt --role "legal"
    ```

*   **Classify all files in a directory:**
    ```bash
    python cli.py --directory ./documents/
    ```

*   **Classify all files in a directory recursively:**
    ```bash
    python cli.py --directory ./documents/ --recursive
    ```

## 4. Storage Locations

Processed files, including classification results and extracted relationships, are stored in a structured directory hierarchy. The base directory for storage is determined by the `DATA_DIR` environment variable.

*   **Output Format**: Results are stored as structured JSON files. Each JSON file contains:
    *   Original content
    *   Metadata (e.g., timestamp, source file path)
    *   Classification results (e.g., categories, tags)
    *   Extracted relationships

*   **Directory Structure**:
    The exact sub-directory structure under `DATA_DIR` would depend on the implementation in [`file_saver.py`](storage/file_saver.py) and [`classification_cache.py`](storage/classification_cache.py), but typically follows a logical organization, possibly by date, classification category, or source.

    Example (conceptual):
    ```
    $DATA_DIR/
    ├── classified_documents/
    │   ├── 2023-10-27/
    │   │   ├── article_123.json
    │   │   └── blog_post_456.json
    │   └── uncategorized/
    │       └── document_789.json
    └── cache/
        ├── document_hash_abc.json
        └── document_hash_xyz.json
## Output JSON Schema

The classification and relationship extraction results are saved in a structured JSON format. Below is the detailed schema of the output JSON files:

```json
{
  "original_document": {
    "source": "string",
    "title": "string",
    "content": "string",
    "url": "string",
    "timestamp": "string (ISO 8601 format)"
  },
  "original_metadata": {
    "source_path": "string",
    "original_filename": "string",
    "timestamp_processed": "string (ISO 8601 format)"
  },
  "classification_results": {
    "section_hierarchy": [
      "string"
    ],
    "tags": [
      "string"
    ],
    "refined_source": "string",
    "collection": "string",
    "topics": [
      "string"
    ],
    "confidence": "number",
    "model_used": "string"
  },
  "relationships": {
    "requires": [
      "string"
    ],
    "integrates_with": [
      "string"
    ],
    "extends": [
      "string"
    ]
  },
  "processing_metadata": {
    "model_used": "string",
    "confidence": "number",
    "processing_time_seconds": "number"
  }
}
```

## Makefile Commands

```bash
make setup    # Install dependencies and verify setup
make test     # Run tests
make verify   # Verify local setup
make clean    # Clean temporary files
```