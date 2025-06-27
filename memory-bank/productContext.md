# Product Context

This file describes the overall product context for the `rag-classification` service, including its purpose, target audience, and key features.

**Purpose:**
The `rag-classification` service is a dedicated microservice designed to provide sophisticated document classification capabilities for the RAG (Retrieval-Augmented Generation) ecosystem. It aims to enhance retrieval accuracy and support code generation workflows by offering intelligent, relationship-aware document categorization.

**Target Audience:**
- **Developers:** Seeking consistent classification, relationship awareness, and role-optimized code intelligence for RAG projects.
- **System Architects:** Requiring isolated classification logic, scalability, and maintainability within the RAG ecosystem.
- **Content Creators/Curators:** Benefiting from automated categorization and relationship extraction for documentation.

**Key Features:**
- **Automated Relationship Extraction:** Detects dependencies, integrations, and prerequisites from code and documentation.
- **Code-Aware Processing:** Specializes in WordPress-specific intelligence (hooks, plugins, blocks, themes) and language-specific processing (PHP, JavaScript, CSS, JSON).
- **Role-Specific Classification:** Optimizes classification for CODE, ARCHITECT, DEBUG, ORCHESTRATOR, and ASK roles.
- **Integration with RAG Ecosystem:** Seamlessly integrates with `rag-scraper` for batch processing and `rag-server` for per-chunk classification and relationship queries.
- **LLM Integration Strategy:** Utilizes DeepSeek V3 API as primary model for cost-efficiency, with OpenRouter for fallback models (GPT-4.5, Claude).
- **Caching and Performance Optimization:** Implements multi-level caching (Redis, PostgreSQL) and async processing for high performance.
- **Robust Error Handling:** Includes graceful degradation and error recovery mechanisms for LLM service unavailability or low confidence.
**Deployment Approach:**
- Hosted on Render.com with automatic dependency installation
- Build process installs all requirements from requirements.txt
- No local dependency installation needed
- Environment fully managed by Render.com infrastructure
**Production Deployment:**
- URL: https://rag-classification.onrender.com
- Health Check: https://rag-classification.onrender.com/api/v1/health
- Fully managed by Render.com infrastructure
- No local development server required