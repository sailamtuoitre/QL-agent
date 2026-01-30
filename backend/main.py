from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import ingestion
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Enterprise Restaurant Revenue Analytics AI Agent API",
    version="0.1.0",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include Routers
app.include_router(ingestion.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["Ingestion"])

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.PROJECT_NAME,
        "mode": settings.MODE
    }

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
