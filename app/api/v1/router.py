"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import workflows

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    workflows.router,
    prefix="/workflows",
    tags=["workflows"]
)

@api_router.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "FlowNinjas Core API v1",
        "version": "0.1.0",
        "docs": "/docs"
    }
