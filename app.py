"""WSGI application entry point for Render deployment."""
from api.main import app

import sys
import os

# Add the src directory to Python path for absolute imports
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# This is the WSGI application that gunicorn will use
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)