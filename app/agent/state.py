from typing import Any, TypedDict


class ReviewState(TypedDict, total=False):
    report: dict[str, Any]
    review: str
