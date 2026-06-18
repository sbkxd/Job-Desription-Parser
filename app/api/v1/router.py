"""API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints.compatibility_api import router as compatibility_router
from app.api.v1.endpoints.extraction import router as extraction_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.normalization import router as normalization_router
from app.api.v1.endpoints.pipeline import router as pipeline_router
from app.api.v1.endpoints.preprocessing import router as preprocessing_router
from app.api.v1.endpoints.recommendations_api import router as recommendations_router
from app.api.v1.endpoints.resume_api import router as resume_router
from app.api.v1.endpoints.review import router as review_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(
    preprocessing_router, prefix="/preprocess", tags=["Preprocessing"]
)
api_router.include_router(extraction_router, prefix="/extract", tags=["Extraction"])
api_router.include_router(
    normalization_router, prefix="/normalize", tags=["Normalization"]
)
api_router.include_router(review_router, prefix="/reviews", tags=["Review"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
api_router.include_router(
    compatibility_router, prefix="/compatibility", tags=["Compatibility"]
)
api_router.include_router(
    recommendations_router, prefix="/resume", tags=["Recommendations"]
)
