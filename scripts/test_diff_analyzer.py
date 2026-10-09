
from app.analyzers.diff_analyzer import analyze_diff


def main():
    sample_pr = {
        "title": "Add login validation",
        "url": "https://github.com/example/project/pull/12",
        "files": [
            {
                "filename": "app/auth.py",
                "status": "modified",
                "additions": 15,
                "deletions": 4,
                "changes": 19,
                "patch": "@@ -1,4 +1,15 @@",
            },
            {
                "filename": "tests/test_auth.py",
                "status": "added",
                "additions": 20,
                "deletions": 0,
                "changes": 20,
                "patch": "@@ -0,0 +1,20 @@",
            },
        ],
    }

    result = analyze_diff(sample_pr)

    print("Diff analyzer test")
    print("------------------")
    print("Title:", result["title"])
    print("Changed files:", result["changed_file_count"])
    print("Additions:", result["total_additions"])
    print("Deletions:", result["total_deletions"])
    print("Total changes:", result["total_changes"])
    print("File types:", result["file_types"])
    print("File statuses:", result["file_statuses"])

    assert result["changed_file_count"] == 2
    assert result["total_additions"] == 35
    assert result["total_deletions"] == 4
    assert result["total_changes"] == 39

    print("\nAll diff analyzer checks passed!")


if __name__ == "__main__":
    main()