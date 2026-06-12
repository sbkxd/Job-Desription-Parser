"""FastAPI router endpoint for triggering the orchestrated parser pipeline."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.orchestration.schemas.schemas import PipelineRequest
from app.orchestration.services.pipeline_service import PipelineService

router = APIRouter()


@router.post(
    "/run",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Run unified parser pipeline",
    description="Runs the unified LangGraph workflow (Ingestion -> Segmentation -> Extraction -> Normalization -> Review) on a URL or PDF.",
)
async def run_pipeline(
    payload: PipelineRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute the full job description parser pipeline."""
    if not payload.url and not payload.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either 'url' or 'pdf_path' must be provided.",
        )

    service = PipelineService(db)
    final_state = await service.run_pipeline(url=payload.url, pdf_path=payload.pdf_path)

    # Convert state to serializable dictionary (filter out non-serializable fields like 'db')
    output = {k: v for k, v in final_state.items() if k != "db"}
    output["success"] = not bool(final_state.get("errors"))

    if final_state.get("errors") and not final_state.get("raw_document"):
        # If execution failed completely (e.g. no document was fetched)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline execution failed: {', '.join(final_state['errors'])}",
        )

    return output
