from typing import Any


def analyze_tests(pull_request: dict[str, Any]) -> dict[str, Any]:
    """Identify test-related files in a pull request."""

    files = pull_request.get("files", [])
    test_files = []
    non_test_files = []

    for file in files:
        filename = file.get("filename", "")
        normalized = filename.lower().replace("\\", "/")
        basename = normalized.rsplit("/", 1)[-1]

        is_test = (
            normalized.startswith(("tests/", "test/"))
            or "/tests/" in normalized
            or basename.startswith("test_")
            or ".test." in basename
            or ".spec." in basename
            or basename.endswith("_test.py")
        )

        if is_test:
            test_files.append(filename)
        else:
            non_test_files.append(filename)

    if test_files:
        status = "test_files_present"
        message = (
            f"Found {len(test_files)} test-related file(s). "
            "Their presence does not confirm that tests pass."
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
