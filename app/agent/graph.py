from langgraph.graph import END, START, StateGraph

from app.agent.nodes import generate_review
from app.agent.state import ReviewState


def build_review_graph():
    """Create the PRNarrator review workflow."""

    workflow = StateGraph(ReviewState)
    workflow.add_node("generate_review", generate_review)
    workflow.add_edge(START, "generate_review")
    workflow.add_edge("generate_review", END)

    return workflow.compile()


review_graph = build_review_graph()


def run_review(report: dict) -> str:
    """Run the graph and return its generated review."""

    result = review_graph.invoke({"report": report})
    return result["review"]
