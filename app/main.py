from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.agent.graph import run_review
from app.github.client import GitHubClientError
from app.services.analysis_service import analyze_pull_request


app = FastAPI(
    title="PRNarrator API",
    description="AI-assisted GitHub pull request analysis and review.",
    version="1.0.0",
)


class AnalyzeRequest(BaseModel):
    pr_url: HttpUrl = Field(
        description="A GitHub pull request URL, such as "
        "https://github.com/owner/repo/pull/123"
    )


class AnalyzeResponse(BaseModel):
    analysis: dict[str, Any]
    ai_review: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "PRNarrator API"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    url = str(request.pr_url)

    try:
        report = analyze_pull_request(url)
        review = run_review(report)
        return AnalyzeResponse(analysis=report, ai_review=review)

    except (ValueError, GitHubClientError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        # Keep internal exception details out of the public API response.
        print(f"PR analysis failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis failed. Check that Ollama is running, "
                "the configured model is available, and the server logs "
                "for details."
            ),
        ) from exc
