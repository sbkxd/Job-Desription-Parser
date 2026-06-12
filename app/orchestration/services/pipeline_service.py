"""Orchestration service driving the LangGraph execution and audit logs."""

import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Job, JobStatus, PipelineEvent, ProcessingRun
from app.orchestration.graph.pipeline_graph import workflow_graph
from app.orchestration.state.state import PipelineState

logger = logging.getLogger(__name__)


class PipelineService:
    """Service driving the LangGraph execution flow and audit trail tracking."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def run_pipeline(
        self, url: Optional[str] = None, pdf_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the LangGraph pipeline and record audit history.

        Args:
            url: Optional JD webpage URL.
            pdf_path: Optional local path to PDF file.

        Returns:
            The final PipelineState dict.
        """
        start_time = time.perf_counter()
        job_id = uuid.uuid4()
        run_id = uuid.uuid4()

        logger.info("Initializing pipeline run %s for job %s", str(run_id), str(job_id))

        # 1. Create a placeholder Job record to satisfy foreign key constraint on processing_runs
        job_record = Job(
            id=job_id,
            title="Processing...",
            status=JobStatus.PROCESSING,
            source_url=url,
        )
        self.session.add(job_record)
        await self.session.flush()

        # 2. Record ProcessingRun start
        run_record = ProcessingRun(
            id=run_id,
            job_id=job_id,
            status="started",
            started_at=datetime.utcnow(),
        )
        self.session.add(run_record)
        await self.session.flush()

        initial_state: PipelineState = {
            "job_source": {
                "url": url,
                "pdf_path": pdf_path,
                "job_id": str(job_id),
            },
            "raw_document": "",
            "segmented_document": {},
            "extraction_result": {},
            "normalization_result": {},
            "review_result": {},
            "mistral_result": {},
            "persistence_result": {},
            "errors": [],
            "execution_metadata": {},
            "db": self.session,
        }

        final_state: dict[str, Any] = {}
        error_msg = None

        try:
            # 2. Invoke LangGraph workflow
            final_state = await workflow_graph.ainvoke(initial_state)

            if final_state.get("errors"):
                error_msg = "; ".join(final_state["errors"])

            # 3. Log pipeline event records for nodes traversed
            metadata = final_state.get("execution_metadata") or {}
            node_metrics = [
                ("fetch", "fetch_duration_ms", "node_fetch_success"),
                ("segment", "segmentation_duration_ms", "node_segment_success"),
                ("extract", "extraction_duration_ms", "node_extract_success"),
                ("normalize", "normalization_duration_ms", "node_normalize_success"),
                ("review_eval", "review_eval_duration_ms", None),
                ("mistral_resolution", "mistral_resolution_duration_ms", None),
                ("review_queue", "review_queue_duration_ms", None),
                ("persistence", "persistence_duration_ms", "node_persist_success"),
            ]

            for node_name, duration_key, success_key in node_metrics:
                if duration_key in metadata:
                    dur = metadata[duration_key]
                    success = True
                    if success_key and success_key in metadata:
                        success = metadata[success_key]

                    event = PipelineEvent(
                        id=uuid.uuid4(),
                        run_id=run_id,
                        node_name=node_name,
                        status="success" if success else "failed",
                        duration_ms=dur,
                    )
                    self.session.add(event)

        except Exception as e:
            error_msg = f"Graph execution crashed: {str(e)}"
            logger.exception("Graph execution error: %s", error_msg)
            if final_state is None:
                final_state = {}

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # 4. Finalize ProcessingRun audit status
        run_record.status = "completed" if not error_msg else "failed"
        run_record.error_message = error_msg
        run_record.duration_ms = duration_ms
        run_record.completed_at = datetime.utcnow()
        if final_state:
            # Exclude non-serializable session database object
            serializable_state = {k: v for k, v in final_state.items() if k != "db"}
            run_record.pipeline_state = serializable_state

        await self.session.flush()

        return final_state
