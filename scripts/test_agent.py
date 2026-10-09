from app.agent.graph import run_review
from app.services.analysis_service import analyze_pull_request


def main():
    url = "https://github.com/fastapi/fastapi/pull/1"

    print("Fetching pull request and running deterministic analysis...")
    report = analyze_pull_request(url)

    print("Generating AI review with local Ollama model...")
    review = run_review(report)

    print("\n" + "=" * 70)
    print("PRNARRATOR AI REVIEW")
    print("=" * 70)
    print(review)
    print("\nLocal LLM review completed successfully!")


if __name__ == "__main__":
    main()
