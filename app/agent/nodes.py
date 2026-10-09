import json
from typing import Any

from langchain_ollama import ChatOllama

from app.agent.prompts import REVIEW_PROMPT
from app.agent.state import ReviewState
from app.config import get_settings


def build_context(report: dict[str, Any]) -> str:
    """Build a compact context from the deterministic analysis report."""

    diff = report.get("diff_summary", {})
    files = []

    for file in diff.get("files", [])[:15]:
        files.append({
            "filename": file.get("filename", ""),
            "status": file.get("status", ""),
            "additions": file.get("additions", 0),
            "deletions": file.get("deletions", 0),
            "patch": (file.get("patch", "") or "")[:1800],
        })

    context = {
        "pull_request": report.get("pull_request", {}),
        "diff_summary": {
            "changed_file_count": diff.get("changed_file_count", 0),
            "total_additions": diff.get("total_additions", 0),
            "total_deletions": diff.get("total_deletions", 0),
            "file_types": diff.get("file_types", {}),
            "files": files,
        },
        "risk_analysis": report.get("risk_analysis", {}),
        "test_analysis": report.get("test_analysis", {}),
    }

    return json.dumps(context, indent=2, ensure_ascii=False)


def generate_review(state: ReviewState) -> dict[str, str]:
    """Generate a reviewer-focused explanation using the local Ollama model."""

    settings = get_settings()
    model = ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,
    )

    prompt = REVIEW_PROMPT.format(context=build_context(state["report"]))
    response = model.invoke(prompt)
    review_text = response.content

    if isinstance(review_text, list):
        review_text = "\n".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in review_text
        )

    review_text = str(review_text).strip()

    if not review_text:
        raise RuntimeError("The local model returned an empty review.")

    return {"review": review_text}
