
from app.analyzers.risk_analyzer import analyze_risk
from app.analyzers.test_analyzer import analyze_tests


def main():
    sample_pr = {
        "files": [
            {
                "filename": "app/auth.py",
                "status": "modified",
                "additions": 15,
                "deletions": 4,
                "patch": "+ validate_user_token()",
            },
            {
                "filename": "tests/test_auth.py",
                "status": "added",
                "additions": 20,
                "deletions": 0,
                "patch": "+ def test_authentication():",
            },
        ]
    }

    diff_summary = {
        "changed_file_count": 2,
        "total_additions": 35,
        "total_deletions": 4,
        "total_changes": 39,
    }

    risk = analyze_risk(sample_pr, diff_summary)
    tests = analyze_tests(sample_pr)

    print("Risk analysis:", risk)
    print("\nTest analysis:", tests)

    assert risk["risk_level"] in {"low", "medium", "high"}
    assert risk["risk_score"] >= 0
    assert tests["test_file_count"] == 1
    assert tests["status"] == "test_files_present"

    print("\nAll analyzer checks passed!")


if __name__ == "__main__":
    main()