from app.analyzers.diff_analyzer import analyze_diff
from app.analyzers.risk_analyzer import analyze_risk
from app.analyzers.test_analyzer import analyze_tests


def test_diff_analyzer_handles_empty_pull_request():
    result = analyze_diff({"files": []})

    assert result["changed_file_count"] == 0
    assert result["total_additions"] == 0
    assert result["total_deletions"] == 0
    assert result["files"] == []


def test_diff_analyzer_counts_changes_and_file_types():
    pr = {
        "title": "Update API",
        "url": "https://github.com/example/repo/pull/1",
        "files": [
            {
                "filename": "app/main.py",
                "status": "modified",
                "additions": 12,
                "deletions": 4,
                "patch": "@@ -1 +1 @@",
            },
            {
                "filename": "tests/test_main.py",
                "status": "added",
                "additions": 8,
                "deletions": 0,
                "patch": "",
            },
        ],
    }

    result = analyze_diff(pr)

    assert result["changed_file_count"] == 2
    assert result["total_additions"] == 20
    assert result["total_deletions"] == 4
    assert result["total_changes"] == 24
    assert result["file_types"] == {".py": 2}
    assert result["file_statuses"] == {"modified": 1, "added": 1}


def test_risk_analyzer_flags_sensitive_production_paths():
    pr = {
        "files": [
            {
                "filename": "app/database/models.py",
                "additions": 10,
                "deletions": 0,
            },
            {
                "filename": "app/auth/login.py",
                "additions": 5,
                "deletions": 0,
            },
        ]
    }
    diff = {
        "changed_file_count": 2,
        "total_additions": 15,
        "total_deletions": 0,
        "total_changes": 15,
    }

    result = analyze_risk(pr, diff)
    categories = {item["category"] for item in result["findings"]}

    assert "database" in categories
    assert "authentication" in categories
    assert result["risk_score"] >= 4


def test_risk_analyzer_does_not_flag_test_paths_as_sensitive_code():
    pr = {
        "files": [
            {
                "filename": "tests/test_database.py",
                "additions": 10,
                "deletions": 0,
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
    categories = {item["category"] for item in result["findings"]}

    assert "database" not in categories
    assert "authentication" not in categories
    assert "security" not in categories


def test_risk_analyzer_reports_insufficient_data():
    result = analyze_risk(
        {"files": []},
        {
            "changed_file_count": 0,
            "total_additions": 0,
            "total_deletions": 0,
            "total_changes": 0,
        },
    )

    assert result["risk_level"] == "low"
    assert any(
        item["category"] == "insufficient_data"
        for item in result["findings"]
    )


def test_test_analyzer_identifies_test_and_production_files():
    pr = {
        "files": [
            {"filename": "tests/test_auth.py"},
            {"filename": "src/user.test.ts"},
            {"filename": "app/main.py"},
            {"filename": "src/user.spec.ts"},
        ]
    }

    result = analyze_tests(pr)

    assert result["test_file_count"] == 3
    assert result["non_test_file_count"] == 1
    assert result["status"] == "test_files_present"
    assert "app/main.py" not in result["test_files"]


def test_test_analyzer_does_not_claim_tests_passed():
    result = analyze_tests(
        {"files": [{"filename": "tests/test_api.py"}]}
    )

    assert "pass" in result["message"].lower()
    assert result["status"] == "test_files_present"
