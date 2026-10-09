from typing import Any

from app.analyzers.diff_analyzer import analyze_diff
from app.analyzers.risk_analyzer import analyze_risk
from app.analyzers.test_analyzer import analyze_tests
from app.github.client import GitHubClient


class AnalysisService:
    """Orchestrate GitHub retrieval and pull request analysis."""

    def __init__(self) -> None:
        self.github_client = GitHubClient()

    def analyze_pull_request(self, pr_url: str) -> dict[str, Any]:
        """Retrieve a PR and produce a combined analysis report."""

        pull_request = self.github_client.get_pull_request(pr_url)

        diff_summary = analyze_diff(pull_request)
        risk_summary = analyze_risk(pull_request, diff_summary)
        test_summary = analyze_tests(pull_request)

        return {
            "pull_request": {
                "url": pull_request["url"],
                "number": pull_request["number"],
                "title": pull_request["title"],
                "author": pull_request["author"],
                "state": pull_request["state"],
                "base_branch": pull_request["base_branch"],
                "head_branch": pull_request["head_branch"],
            },
            "diff_summary": diff_summary,
            "risk_analysis": risk_summary,
            "test_analysis": test_summary,
        }


def analyze_pull_request(pr_url: str) -> dict[str, Any]:
    """Convenience function for API routes and scripts."""
    return AnalysisService().analyze_pull_request(pr_url)
