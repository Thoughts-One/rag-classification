from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .routes import classification, relationships, health, batch
from .middleware import auth, rate_limiting, logging

app = FastAPI(
    title="RAG Classification Service",
    description="Document classification and relationship extraction for RAG ecosystem",
    version="0.1.0"
)

@app.get("/")
async def root():
    return JSONResponse(
        content={"status": "running", "service": "RAG Classification API"},
        status_code=200
    )

# Include routers
app.include_router(classification.router)
app.include_router(relationships.router)
app.include_router(health.router, prefix="/api/v1")
app.include_router(batch.router)

# Add middleware
app.middleware("http")(auth.api_key_auth)
app.middleware("http")(rate_limiting.rate_limit_middleware)
app.middleware("http")(logging.request_logger)