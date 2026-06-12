"""LangGraph workflow definition for the unified JD parsing pipeline."""

import logging
import os

from langgraph.graph import END, StateGraph

from app.orchestration.nodes.extract_node import extract_node
from app.orchestration.nodes.fetch_node import fetch_jd_node
from app.orchestration.nodes.mistral_resolution_node import mistral_resolution_node
from app.orchestration.nodes.normalize_node import normalize_node
from app.orchestration.nodes.persistence_node import persistence_node
from app.orchestration.nodes.review_eval_node import review_eval_node
from app.orchestration.nodes.review_queue_node import review_queue_node
from app.orchestration.nodes.segment_node import segment_node
from app.orchestration.routing.router import review_router
from app.orchestration.state.state import PipelineState

logger = logging.getLogger(__name__)


def build_pipeline_graph() -> StateGraph[PipelineState]:
    """Construct and configure the LangGraph workflow structure.

    Returns:
        Compiled StateGraph.
    """
    builder = StateGraph(PipelineState)

    # 1. Register Nodes
    builder.add_node("fetch", fetch_jd_node)
    builder.add_node("segment", segment_node)
    builder.add_node("extract", extract_node)
    builder.add_node("normalize", normalize_node)
    builder.add_node("review_eval", review_eval_node)
    builder.add_node("mistral_resolution", mistral_resolution_node)
    builder.add_node("review_queue", review_queue_node)
    builder.add_node("persistence", persistence_node)

    # 2. Configure Entrypoint and Static Edges
    builder.set_entry_point("fetch")
    builder.add_edge("fetch", "segment")
    builder.add_edge("segment", "extract")
    builder.add_edge("extract", "normalize")
    builder.add_edge("normalize", "review_eval")

    # 3. Configure Conditional Routing
    builder.add_conditional_edges(
        "review_eval",
        review_router,
        {
            "mistral_resolution": "mistral_resolution",
            "persistence": "persistence",
        },
    )

    # 4. Configure Fallback Path static edges
    builder.add_edge("mistral_resolution", "review_queue")
    builder.add_edge("review_queue", "persistence")
    builder.add_edge("persistence", END)

    return builder


# Compile the graph
workflow_graph = build_pipeline_graph().compile()

# Generate Mermaid and save to docs/graphs/ on import to keep documentation in sync
try:
    mermaid_diagram = workflow_graph.get_graph().draw_mermaid()
    docs_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "docs",
        "graphs",
    )
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, "pipeline_flow.md"), "w", encoding="utf-8") as f:
        f.write("# Pipeline Flow Graph\n\n```mermaid\n" + mermaid_diagram + "\n```\n")
    logger.info("Saved graph visualization to docs/graphs/pipeline_flow.md")
except Exception as e:
    logger.warning("Failed to generate graph visualization: %s", str(e))
