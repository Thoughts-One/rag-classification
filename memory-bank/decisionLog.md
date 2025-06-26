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