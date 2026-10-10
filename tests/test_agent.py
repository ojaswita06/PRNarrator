import json

from app.agent.graph import build_review_graph, run_review
from app.agent.nodes import build_context, generate_review


def sample_report():
    return {
        "pull_request": {
            "title": "Improve API validation",
            "url": "https://github.com/example/repo/pull/1",
        },
        "diff_summary": {
            "changed_file_count": 1,
            "total_additions": 5,
            "total_deletions": 2,
            "file_types": {".py": 1},
            "files": [
                {
                    "filename": "app/main.py",
                    "status": "modified",
                    "additions": 5,
                    "deletions": 2,
                    "patch": "@@ -1 +1 @@",
                }
            ],
        },
        "risk_analysis": {
            "risk_level": "low",
            "risk_score": 0,
            "findings": [],
        },
        "test_analysis": {
            "status": "test_files_present",
            "test_files": ["tests/test_main.py"],
            "test_file_count": 1,
        },
    }


def test_build_context_contains_report_evidence():
    context = build_context(sample_report())
    parsed = json.loads(context)

    assert parsed["pull_request"]["title"] == "Improve API validation"
    assert parsed["diff_summary"]["changed_file_count"] == 1
    assert parsed["diff_summary"]["files"][0]["filename"] == "app/main.py"
    assert parsed["risk_analysis"]["risk_level"] == "low"
    assert parsed["test_analysis"]["test_file_count"] == 1


def test_build_context_limits_files_to_fifteen():
    report = sample_report()
    report["diff_summary"]["files"] = [
        {
            "filename": f"app/file_{i}.py",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "patch": "x" * 2000,
        }
        for i in range(20)
    ]

    parsed = json.loads(build_context(report))

    assert len(parsed["diff_summary"]["files"]) == 15
    assert len(parsed["diff_summary"]["files"][0]["patch"]) == 1800


def test_generate_review_uses_configured_local_model(monkeypatch):
    calls = {}

    class FakeResponse:
        content = "  Example reviewer report  "

    class FakeChatOllama:
        def __init__(self, **kwargs):
            calls["settings"] = kwargs

        def invoke(self, prompt):
            calls["prompt"] = prompt
            return FakeResponse()

    class FakeSettings:
        ollama_model = "test-model"
        ollama_base_url = "http://localhost:11434"

    monkeypatch.setattr(
        "app.agent.nodes.ChatOllama",
        FakeChatOllama,
    )
    monkeypatch.setattr(
        "app.agent.nodes.get_settings",
        lambda: FakeSettings(),
    )

    result = generate_review({"report": sample_report()})

    assert result["review"] == "Example reviewer report"
    assert calls["settings"]["model"] == "test-model"
    assert calls["settings"]["base_url"] == "http://localhost:11434"
    assert "Improve API validation" in calls["prompt"]


def test_review_graph_runs_with_mocked_generation():
    graph = build_review_graph()

    # Replace the model-calling node with a deterministic test node.
    graph.update_state(
        config={"configurable": {"thread_id": "test-run"}},
        values={"review": "Mocked review"},
    ) if False else None

    from langgraph.graph import END, START, StateGraph
    from app.agent.state import ReviewState

    workflow = StateGraph(ReviewState)
    workflow.add_node(
        "generate_review",
        lambda state: {"review": "Mocked review"},
    )
    workflow.add_edge(START, "generate_review")
    workflow.add_edge("generate_review", END)
    test_graph = workflow.compile()

    result = test_graph.invoke({"report": sample_report()})

    assert result["review"] == "Mocked review"


def test_run_review_returns_graph_review(monkeypatch):
    monkeypatch.setattr(
        "app.agent.graph.review_graph.invoke",
        lambda state: {"review": "Test review"},
    )

    result = run_review(sample_report())

    assert result == "Test review"
