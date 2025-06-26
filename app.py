"""WSGI application entry point for Render deployment."""
from api.main import app

# This is the WSGI application that gunicorn will use
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)