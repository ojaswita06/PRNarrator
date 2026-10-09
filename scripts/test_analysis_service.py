from app.services.analysis_service import analyze_pull_request


def main():
    url = "https://github.com/fastapi/fastapi/pull/1"

    print("Analyzing pull request...")
    report = analyze_pull_request(url)

    pr = report["pull_request"]
    diff = report["diff_summary"]
    risk = report["risk_analysis"]
    tests = report["test_analysis"]

    print("\n=== Pull Request ===")
    print("Title:", pr["title"])
    print("Author:", pr["author"])
    print("State:", pr["state"])

    print("\n=== Diff Summary ===")
    print("Files changed:", diff["changed_file_count"])
    print("Additions:", diff["total_additions"])
    print("Deletions:", diff["total_deletions"])
    print("File types:", diff["file_types"])

    print("\n=== Risk Analysis ===")
    print("Risk level:", risk["risk_level"])
    print("Risk score:", risk["risk_score"])
    print("Findings:", len(risk["findings"]))

    print("\n=== Test Analysis ===")
    print("Status:", tests["status"])
    print("Test files:", tests["test_files"])

    assert pr["title"]
    assert isinstance(diff["files"], list)
    assert risk["risk_level"] in {"low", "medium", "high"}
    assert "status" in tests

    print("\nEnd-to-end analysis pipeline passed!")


if __name__ == "__main__":
    main()
