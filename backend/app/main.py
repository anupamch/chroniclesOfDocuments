import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.api.admin_routes import router as admin_router
from app.api.legal_routes import router as legal_router
from app.services.mongodb import mongodb
from app.core.startup_check import check_configuration_on_startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("\n" + "="*60)
    print("Chronicles of Documents API - Starting")
    print("="*60 + "\n")

    # Check LLM configuration (Ollama or HuggingFace)
    try:
        check_configuration_on_startup()
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}")
        raise

    await mongodb.connect()

    yield

    # Shutdown
    await mongodb.disconnect()
    print("\nAPI Shutdown")


app = FastAPI(
    title="Chronicles of Documents API",
    description="Multi-agentic document analysis system with timeline generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(legal_router, prefix="/api", tags=["legal"])
app.include_router(router, prefix="/api", tags=["documents"])


@app.get("/")
async def root():
    return {
        "message": "Chronicles of Documents API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
