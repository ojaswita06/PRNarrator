# PRNarrator

**AI-assisted GitHub pull request analysis and review**, powered by Python, FastAPI, LangGraph, Ollama, and Streamlit.

PRNarrator retrieves a GitHub pull request, summarizes its changed files, surfaces heuristic review-risk signals, identifies test-related files, and generates a reviewer-focused report using a local language model.

## Features

- **GitHub integration:** Retrieve pull request metadata, changed files, and available diff patches through the GitHub REST API.
- **Change summaries:** Count additions and deletions, group file extensions, and list changed files.
- **Heuristic risk analysis:** Highlight selected sensitive production paths and unusually large or wide changes.
- **Test-file detection:** Identify common test-file naming conventions without claiming that tests passed.
- **Local LLM review:** Generate a structured review with Ollama and LangGraph.
- **FastAPI backend:** Expose health and pull-request analysis endpoints.
- **Streamlit frontend:** View summaries, risk findings, changed files, and the generated review.

## Architecture

```text
GitHub Pull Request URL
          |
          v
    GitHub REST API
          |
          v
  Analysis Service
    |     |      |
    v     v      v
   Diff  Risk   Test-file
 Analysis Analysis Detection
          |
          v
   Structured Report
          |
          v
    LangGraph Agent
          |
          v
   Ollama Local LLM
          |
          v
      FastAPI
          |
          v
     Streamlit UI
```

## Requirements

- Python 3.11 or a compatible supported Python version
- Git
- [Ollama](https://ollama.com/download)
- The `qwen2.5:3b` model, or another compatible model configured through `.env`

## Setup on Windows

Clone the repository and enter its directory:

```powershell
git clone https://github.com/ojaswita06/PRNarrator.git
cd PRNarrator
```

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Make sure Ollama is running, then download the model:

```powershell
ollama pull qwen2.5:3b
ollama list
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` if necessary. A GitHub token is optional for public repositories. Never commit `.env` or publish credentials.

## Run the application

Open two terminals in the project directory and activate `.venv` in both.

Terminal 1 — API:

```powershell
uvicorn app.main:app --reload
```

API health check: http://127.0.0.1:8000/health

Interactive API documentation: http://127.0.0.1:8000/docs

Terminal 2 — Streamlit:

```powershell
streamlit run frontend/app.py
```

Open the local URL printed by Streamlit, usually http://localhost:8501. Paste a GitHub pull request URL and select **Analyze pull request**.

## API

### `GET /health`

Returns the service health status.

### `POST /analyze`

Request:

```json
{
  "pr_url": "https://github.com/fastapi/fastapi/pull/1"
}
```

Returns the structured analysis and AI-generated review.

## Tests

Run the automated tests from the project root:

```powershell
python -m pytest -q
```

The tests cover change aggregation, test-file detection, risk-analysis behavior, and GitHub pull request URL parsing.

## Limitations

- Risk analysis is a transparent heuristic based on selected file paths and change size. It is not a security scanner and cannot prove that a vulnerability exists or that code is safe.
- Test-file detection does not execute tests or verify their results.
- GitHub may omit patch content for binary files, large diffs, or certain file types.
- The LLM's review is generated from the available metadata and patch excerpts. It can still make mistakes; reviewers should verify important claims against the source code.
- The current agent produces a review report; it does not approve, merge, or modify pull requests.
- Public GitHub API requests are subject to rate limits.

## Security

Keep tokens and credentials out of source control. Treat pull request content as untrusted input, and independently verify generated recommendations before acting on them.

## License

Choose and add a license before distributing the project. Until a license is included, do not assume others have permission to reuse the code.
