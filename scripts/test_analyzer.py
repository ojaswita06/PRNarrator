
from typing import Any


TEST_INDICATORS = (
    "test_",
    "_test.",
    ".test.",
    ".spec.",
    "/tests/",
    "\\tests\\",
    "__tests__/",
)


def analyze_tests(pull_request: dict[str, Any]) -> dict[str, Any]:
    """Identify test-related files in a pull request."""

    files = pull_request.get("files", [])
    test_files = []
    non_test_files = []

    for file in files:
        filename = file.get("filename", "")
        normalized = filename.lower().replace("\\", "/")

        is_test = (
            normalized.startswith(("tests/", "test/"))
            or "/tests/" in normalized
            or any(
                indicator.replace("\\", "/") in normalized
                for indicator in TEST_INDICATORS
            )
        )

        if is_test:
            test_files.append(filename)
        else:
            non_test_files.append(filename)

    if test_files:
        status = "test_files_present"
        message = (
            f"Found {len(test_files)} test-related file(s). "
            "This does not confirm that the tests pass."
        )
    else:
        status = "no_test_files_detected"
        message = (
            "No test-related files were detected among the changed files. "
            "Tests may exist elsewhere in the repository."
        )

    return {
        "status": status,
        "test_files": test_files,
        "test_file_count": len(test_files),
        "non_test_file_count": len(non_test_files),
        "message": message,
    }