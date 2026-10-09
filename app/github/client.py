
import re
from typing import Any
from urllib.parse import urlparse

import httpx

from app.config import get_settings


class GitHubClientError(Exception):
    """Raised when a GitHub API request fails."""


class GitHubClient:
    """Client for retrieving GitHub pull request metadata and diffs."""

    API_BASE = "https://api.github.com"

    def __init__(self) -> None:
        settings = get_settings()

        token = (
            settings.github_token.get_secret_value().strip()
            if settings.github_token
            else ""
        )

        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @staticmethod
    def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
        """Parse a GitHub pull request URL into owner, repo, and PR number."""
        parsed = urlparse(pr_url.strip())

        if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
            raise ValueError(
                "Provide a valid URL such as "
                "https://github.com/owner/repo/pull/123"
            )

        match = re.fullmatch(
            r"/([^/]+)/([^/]+)/pull/(\d+)/?",
            parsed.path,
        )

        if not match:
            raise ValueError(
                "Invalid pull request URL. Expected "
                "https://github.com/owner/repo/pull/123"
            )

        owner, repo, number = match.groups()
        return owner, repo, int(number)

    def _get(self, endpoint: str) -> Any:
        """Send a GET request to the GitHub REST API."""
        try:
            response = httpx.get(
                f"{self.API_BASE}{endpoint}",
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True,
            )
        except httpx.HTTPError as exc:
            raise GitHubClientError(
                f"Unable to connect to GitHub: {exc}"
            ) from exc

        if response.status_code == 401:
            raise GitHubClientError(
                "GitHub authentication failed. Check your GITHUB_TOKEN."
            )

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                raise GitHubClientError(
                    "GitHub API rate limit exceeded. Try again later "
                    "or configure a GitHub token in .env."
                )
            raise GitHubClientError(
                "GitHub denied the request. Check repository permissions "
                "and API rate limits."
            )

        if response.status_code == 404:
            raise GitHubClientError(
                "Pull request or repository not found, or access is restricted."
            )

        if response.is_error:
            raise GitHubClientError(
                f"GitHub API returned HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise GitHubClientError(
                "GitHub returned an invalid JSON response."
            ) from exc

    def get_pull_request(self, pr_url: str) -> dict[str, Any]:
        """Fetch pull request details and up to 100 changed files."""
        owner, repo, number = self.parse_pr_url(pr_url)

        endpoint = f"/repos/{owner}/{repo}/pulls/{number}"
        pr = self._get(endpoint)

        if not isinstance(pr, dict):
            raise GitHubClientError(
                "GitHub returned an unexpected pull request response."
            )

        files_response = self._get(f"{endpoint}/files?per_page=100")

        if not isinstance(files_response, list):
            raise GitHubClientError(
                "GitHub returned an unexpected changed-files response."
            )

        files = [
            {
                "filename": item.get("filename", ""),
                "status": item.get("status", ""),
                "additions": item.get("additions", 0),
                "deletions": item.get("deletions", 0),
                "changes": item.get("changes", 0),
                "patch": item.get("patch") or "",
            }
            for item in files_response
        ]

        return {
            "url": pr.get("html_url", pr_url),
            "number": pr["number"],
            "title": pr.get("title") or "",
            "body": pr.get("body") or "",
            "state": pr.get("state") or "",
            "author": (pr.get("user") or {}).get("login", "unknown"),
            "base_branch": (pr.get("base") or {}).get("ref", ""),
            "head_branch": (pr.get("head") or {}).get("ref", ""),
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
            "changed_file_count": pr.get(
                "changed_files", len(files)
            ),
            "files": files,
        }