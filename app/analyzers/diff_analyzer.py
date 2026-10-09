
from collections import Counter
from typing import Any


def analyze_diff(pull_request: dict[str, Any]) -> dict[str, Any]:
    """Summarize changed files and additions/deletions from a GitHub PR."""

    files = pull_request.get("files", [])

    file_types = Counter()
    file_statuses = Counter()
    total_additions = 0
    total_deletions = 0
    total_changes = 0
    diff_sections = []

    for file in files:
        filename = file.get("filename", "unknown")
        status = file.get("status", "modified")
        additions = int(file.get("additions", 0) or 0)
        deletions = int(file.get("deletions", 0) or 0)
        patch = file.get("patch", "") or ""

        extension = (
            "." + filename.rsplit(".", 1)[-1].lower()
            if "." in filename.rsplit("/", 1)[-1]
            else "[no extension]"
        )

        file_types[extension] += 1
        file_statuses[status] += 1
        total_additions += additions
        total_deletions += deletions
        total_changes += additions + deletions

        diff_sections.append(
            {
                "filename": filename,
                "status": status,
                "additions": additions,
                "deletions": deletions,
                "patch": patch,
            }
        )

    return {
        "title": pull_request.get("title", ""),
        "url": pull_request.get("url", ""),
        "changed_file_count": len(files),
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "total_changes": total_changes,
        "file_types": dict(file_types),
        "file_statuses": dict(file_statuses),
        "files": diff_sections,
    }