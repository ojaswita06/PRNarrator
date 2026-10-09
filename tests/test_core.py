from app.analyzers.diff_analyzer import analyze_diff
from app.analyzers.risk_analyzer import analyze_risk
from app.analyzers.test_analyzer import analyze_tests
from app.github.client import GitHubClient


def test_diff_analyzer_counts_changes():
    pr = {
        "title": "Example PR",
        "url": "https://github.com/example/repo/pull/1",
        "files": [
            {
                "filename": "app/main.py",
                "status": "modified",
                "additions": 10,
                "deletions": 3,
                "patch": "@@ -1 +1 @@",
            },
            {
                "filename": "tests/test_main.py",
                "status": "added",
                "additions": 5,
                "deletions": 0,
                "patch": "",
            },
        ],
    }

    result = analyze_diff(pr)

    assert result["changed_file_count"] == 2
    assert result["total_additions"] == 15
    assert result["total_deletions"] == 3
    assert result["total_changes"] == 18


def test_test_analyzer_detects_test_files():
    pr = {
        "files": [
            {"filename": "tests/test_auth.py"},
            {"filename": "app/auth.py"},
            {"filename": "src/user.test.ts"},
        ]
    }

    result = analyze_tests(pr)

    assert result["test_file_count"] == 2
    assert "tests/test_auth.py" in result["test_files"]
    assert "src/user.test.ts" in result["test_files"]


def test_risk_analyzer_does_not_flag_test_files_as_database_code():
    pr = {
        "files": [
            {
                "filename": "tests/test_path.py",
                "additions": 235,
                "deletions": 0,
                "patch": "def test_query_parameter(): pass",
            },
            {
                "filename": "tests/main.py",
                "additions": 0,
                "deletions": 0,
                "patch": "",
            },
        ]
    }
    diff = {
        "changed_file_count": 2,
        "total_additions": 235,
        "total_deletions": 0,
        "total_changes": 235,
    }

    result = analyze_risk(pr, diff)

    categories = {finding["category"] for finding in result["findings"]}
    assert "database" not in categories
    assert "authentication" not in categories
    assert "large_change" in categories


def test_risk_analyzer_flags_database_path():
    pr = {
        "files": [
            {
                "filename": "app/database/models.py",
                "additions": 10,
                "deletions": 0,
                "patch": "",
            }
        ]
    }
    diff = {
        "changed_file_count": 1,
        "total_additions": 10,
        "total_deletions": 0,
        "total_changes": 10,
    }

    result = analyze_risk(pr, diff)

    assert any(
        finding["category"] == "database"
        for finding in result["findings"]
    )


def test_github_client_rejects_non_pr_urls():
    import pytest

    with pytest.raises(ValueError):
        GitHubClient.parse_pr_url("https://github.com/example/repo")


def test_github_client_parses_pr_url():
    assert GitHubClient.parse_pr_url(
        "https://github.com/fastapi/fastapi/pull/1"
    ) == ("fastapi", "fastapi", 1)
