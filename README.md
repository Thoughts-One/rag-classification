# RAG Classification Service

A microservice for document classification and relationship extraction in the RAG ecosystem.

## Features

- Document classification with role-specific optimization
- Relationship extraction (dependencies, integrations)
- Code-aware processing for technical documentation
- Multi-model LLM integration with fallback
- Caching and performance optimization

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DEEPSEEK_API_KEY=your_key
export OPENROUTER_API_KEY=your_key
export API_KEY=your_service_key
```

3. Run the service:
```bash
uvicorn api.main:app --reload
```

## API Documentation

Available at `http://localhost:8000/docs` when the service is running.

## Deployment

Build Docker image:
```bash
docker build -t rag-classification .
```

Run container:
```bash
docker run -p 8000:8000 rag-classification
```

## Configuration

Edit the YAML files in `config/` to customize:
- Classification taxonomy
- Relationship extraction patterns
- Role-specific processing
