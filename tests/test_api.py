from fastapi.testclient import TestClient

import app.main as main_module


client = TestClient(main_module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint_returns_analysis_and_review(monkeypatch):
    expected_analysis = {
        "title": "Example PR",
        "risk_analysis": {
            "risk_level": "low",
            "risk_score": 0,
            "findings": [],
        },
    }

    monkeypatch.setattr(
        main_module,
        "analyze_pull_request",
        lambda url: expected_analysis,
    )
    monkeypatch.setattr(
        main_module,
        "run_review",
        lambda report: "Example AI review",
    )

    response = client.post(
        "/analyze",
        json={
            "pr_url": "https://github.com/example/repo/pull/1"
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["analysis"] == expected_analysis
    assert body["ai_review"] == "Example AI review"


def test_analyze_endpoint_rejects_invalid_url():
    response = client.post(
        "/analyze",
        json={"pr_url": "not-a-github-url"},
    )

    assert response.status_code == 422


def test_analyze_endpoint_handles_analysis_failure(monkeypatch):
    def fail_analysis(url):
        raise RuntimeError("Simulated test failure")

    monkeypatch.setattr(
        main_module,
        "analyze_pull_request",
        fail_analysis,
    )

    response = client.post(
        "/analyze",
        json={
            "pr_url": "https://github.com/example/repo/pull/1"
        },
    )

    assert response.status_code == 500
    assert "Simulated test failure" not in response.text
