# Decision Log

This file logs important decisions made during the project, including the rationale and alternatives considered.
[2025-06-26 08:45:00] - Render.com Deployment Debugging Session

**Problem**: Multiple deployment failures with gunicorn command not found and module import errors.

**Root Cause Analysis**: 
1. Render.com uses default gunicorn commands that override custom start commands
2. Default command expects 'your_application.wsgi' module structure
3. FastAPI apps need proper WSGI/ASGI adapter for gunicorn

**Solutions Attempted**:
1. Custom uvicorn start commands - FAILED (Render ignores custom commands)
2. Gunicorn with uvicorn workers - FAILED (PATH and command issues)
3. Adding gunicorn to requirements.txt - PARTIAL SUCCESS (gunicorn found but wrong module)

**Final Solution**: 
- Add gunicorn==23.0.0 to requirements.txt
- Create app.py with proper WSGI application export
- Use Render's default Python 3.13.4
- Let Render use default gunicorn app:application command

**Key Learnings**:
- Render.com strongly prefers standard deployment patterns
- Custom start commands are often ignored in favor of platform defaults
- WSGI entry point must be named 'application' in root-level module
- Modern dependency versions work better than trying to force older ones
[2025-06-26 09:58:15] - Updated API health check routing and security:
- Added /api/v1 prefix to health router in main.py
- Secured API_KEY in render.yaml with sync:false
- Verified auth middleware health check paths match /api/v1/health
[2025-06-26 10:42:20] - Simplified health check endpoints to be extremely lightweight by removing all system checks from /health/detailed endpoint to minimize Render.com health check overhead
[2025-06-26 10:46:53] - Modified request logging middleware to filter out Render.com health checks (User-Agent: "Render/1.0") to reduce log noise. Health checks occur every 5 seconds and were cluttering logs.

## Coding Doctrine: **Incremental Development with Continuous Validation**

### Primary Principles:

**1. Minimum Viable Implementation (MVI)**
- Implement the smallest possible code change that delivers a complete, testable feature increment
- Each change should be independently verifiable and deployable

**2. Red-Green-Refactor Cycles (TDD-inspired)**
- Write failing test → Write minimal code to pass → Refactor → Repeat
- Even without strict TDD, maintain this rhythm of test-implement-verify

**3. Vertical Slicing**
- Cut features into thin vertical slices that touch all necessary layers (UI → business logic → data)
- Each slice delivers end-to-end functionality, however minimal

### Supporting Practices:

**Atomic Commits & Feature Branches**
- Each commit represents a complete, working unit
- Commits should compile, pass tests, and not break existing functionality

**Walking Skeleton Approach**
- Start with the thinnest possible end-to-end implementation
- Gradually flesh out functionality while maintaining working state

**Fail-Fast Feedback Loops**
- Integrate and test frequently (ideally after each small change)
- Catch issues early when context is fresh and fixes are simple

**YAGNI Principle (You Aren't Gonna Need It)**
- Implement only what's immediately needed for the current increment
- Avoid anticipatory complexity

### Practical Implementation:

- **Feature decomposition**: Break large features into independently deliverable micro-features
- **Time-boxing**: Set short development cycles (30min-2hrs) before testing
- **Integration checkpoints**: Verify the system works after each increment
- **Evolutionary design**: Let architecture emerge through small, validated changes

This doctrine is often called **"Baby Steps Development"** or **"Micro-Increment Development"** in agile contexts.
[2025-06-26 11:56:45] - Implemented OpenRouter API client with DeepSeek V3 as primary model and fallback support. Moved OpenRouter-specific logic to dedicated openrouter_client.py and updated llm_client.py to use it.
[2025-06-26 11:59:45] - Migrated document preprocessing functions from rag-server to rag-classification/utils/text_processing.py. Includes validate_document(), process_json_file(), and process_markdown_file() functions while maintaining existing text processing capabilities.
[2025-06-26 12:06:33] - Implemented SQLite caching system for classification results and relationship metadata
- Replaced Redis with SQLite in classification_cache.py
- Maintained same interface (get, set, clear) for backward compatibility
- Added proper connection management and environment variable configuration
- Integrated caching into API routes (classification.py, relationships.py)
- Database path configurable via DATABASE_URL environment variable
- Cache TTL configurable via CACHE_TTL_HOURS environment variable
[2025-06-26 12:12:30] - Implemented core error handling system
- Created error_handling.py with ClassificationError, LLMServiceError, ValidationError, ConfidenceError exceptions
- Implemented ErrorSeverity Enum for error classification
- Built ErrorHandler class with handle_error method and specific fallback strategies
- Integrated with LLMClient while avoiding circular dependencies
- Added rule-based fallback mechanism for service degradation
[2025-06-26 12:34:11] - Implemented RelationshipExtractor class with regex patterns for requires, integrates_with, extends, related_to, and prerequisites relationships. Integrated into DocumentClassifier workflow.