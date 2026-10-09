import re
from typing import Any


# These patterns apply to production file paths, not test filenames or
# arbitrary words found in a diff.
SENSITIVE_PATHS = {
    "authentication": re.compile(
        r"(^|/)(auth|authentication|login|oauth|sessions?)(/|\.|$)|"
        r"(^|/)(permissions?|access_control)(/|\.|$)",
        re.IGNORECASE,
    ),
    "security": re.compile(
        r"(^|/)(security|cryptography|crypto|secrets?)(/|\.|$)|"
        r"(^|/)(middleware|csrf)(/|\.|$)",
        re.IGNORECASE,
    ),
    "database": re.compile(
        r"(^|/)(db|database|migrations?|repositories|models)(/|\.|$)|"
        r"(^|/)[^/]+\.(sql|prisma)$",
        re.IGNORECASE,
    ),
    "infrastructure": re.compile(
        r"(^|/)(dockerfile|docker-compose[^/]*|terraform|\.github/workflows)(/|$)|"
        r"(^|/)[^/]+\.(ya?ml)$",
        re.IGNORECASE,
    ),
}

TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__)(/|$)|"
    r"(^|/)(test_[^/]*|[^/]*_test\.py|[^/]*\.(test|spec)\.[^/]+)$",
    re.IGNORECASE,
)


def analyze_risk(
    pull_request: dict[str, Any],
    diff_summary: dict[str, Any],
) -> dict[str, Any]:
    """Estimate review risk using file paths and overall change size.

    This is a transparent heuristic, not a vulnerability scanner.
    """

    findings: list[dict[str, Any]] = []
    score = 0
    files = pull_request.get("files", [])
    seen: set[tuple[str, str]] = set()

    for file in files:
        filename = (file.get("filename") or "").replace("\\", "/").lstrip("./")

        # Tests can be important, but their filenames alone should not be
        # classified as production authentication, database, or security code.
        if not filename or TEST_PATH.search(filename):
            continue

        for category, pattern in SENSITIVE_PATHS.items():
            if pattern.search(filename):
                key = (category, filename)
                if key in seen:
                    continue

                seen.add(key)
                score += 2
                findings.append({
                    "category": category,
                    "file": filename,
                    "reason": (
                        f"The changed file path indicates the "
                        f"{category} area may need careful review."
                    ),
                })

    total_changes = int(
        diff_summary.get(
            "total_changes",
            int(diff_summary.get("total_additions", 0))
            + int(diff_summary.get("total_deletions", 0)),
        )
    )
    changed_files = int(diff_summary.get("changed_file_count", len(files)))

    if total_changes >= 500:
        score += 3
        findings.append({
            "category": "large_change",
            "file": None,
            "reason": f"Large change set: {total_changes} lines changed.",
        })
    elif total_changes >= 200:
        score += 2
        findings.append({
            "category": "large_change",
            "file": None,
            "reason": (
                f"Moderately large change set: "
                f"{total_changes} lines changed."
            ),
        })

    if changed_files >= 20:
        score += 2
        findings.append({
            "category": "wide_scope",
            "file": None,
            "reason": f"The PR modifies {changed_files} files.",
        })

    if not files:
        findings.append({
            "category": "insufficient_data",
            "file": None,
            "reason": "No changed-file data is available for risk analysis.",
        })

    level = "high" if score >= 6 else "medium" if score >= 3 else "low"

    return {
        "risk_level": level,
        "risk_score": score,
        "findings": findings,
        "total_changes": total_changes,
        "changed_files": changed_files,
        "note": (
            "Heuristic estimate based on changed file paths and change size. "
            "It does not establish that a vulnerability exists or that "
            "the code is safe."
        ),
    }

