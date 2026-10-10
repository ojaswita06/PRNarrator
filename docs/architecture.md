# PRNarrator Architecture

## Overview

PRNarrator is an AI-assisted GitHub pull request analysis application. It combines deterministic analysis with a local large language model to produce structured, reviewer-focused reports.

## System Components

### 1. Streamlit Frontend

The frontend, implemented in `frontend/app.py`, provides the user interface. Users submit a GitHub pull request URL and view the generated review, changed files, risk signals, and test-related file information.

### 2. FastAPI Backend

The API is implemented in `app/main.py`.

* `GET /health` reports the service health.
* `POST /analyze` accepts a GitHub pull request URL and orchestrates the analysis workflow.
* Request validation is handled by Pydantic.
* API errors are returned through appropriate HTTP responses.

### 3. GitHub Client

`app/github/client.py` retrieves pull request metadata and changed-file information from GitHub. An optional GitHub personal access token can be configured to improve API rate limits.

### 4. Deterministic Analysis

The analysis service and analyzers inspect the pull request before AI generation.

* Diff analysis summarizes changed files, additions, and deletions.
* Risk analysis calculates heuristic risk signals based on change characteristics.
* Test analysis identifies files that appear related to testing.

These signals support review prioritization. They do not prove that a vulnerability exists, that code is safe, or that tests have passed.

### 5. LangGraph Review Workflow

The workflow is defined in `app/agent/graph.py`. It passes the analysis report to the review-generation node in `app/agent/nodes.py`.

The node builds a compact context, applies the review prompt, and invokes the configured Ollama model.

### 6. Local Language Model

PRNarrator uses Ollama with `qwen2.5:3b` by default. The model and Ollama base URL can be configured through environment variables.

The model generates a natural-language explanation from the available analysis evidence. Its output should be reviewed by a human before making engineering decisions.

## Request Flow

1. The user submits a GitHub pull request URL through Streamlit.
2. The frontend sends the request to the FastAPI backend.
3. The GitHub client retrieves pull request metadata and changed files.
4. The analysis service runs the diff, risk, and test analyzers.
5. The resulting report is passed to the LangGraph workflow.
6. The workflow invokes the local Ollama model to generate the review.
7. The API returns structured analysis and the AI-generated review.
8. The frontend displays the results.

## Deployment

Docker Compose runs two services:

* **API:** FastAPI, exposed on host port `8000`.
* **Frontend:** Streamlit, exposed on host port `8502` by default in this local setup.

The API container connects to Ollama running on the host machine. The model must be available locally, and the Ollama service must be reachable from the API container.

## Configuration

* `GITHUB_TOKEN`: Optional GitHub personal access token.
* `OLLAMA_MODEL`: Ollama model name, default `qwen2.5:3b`.
* `OLLAMA_BASE_URL`: Ollama API base URL, default `http://localhost:11434` for local execution.

Do not commit `.env` or credentials to version control. Use `.env.example` as the configuration template.

## Limitations

* Risk scores are heuristic estimates, not security guarantees.
* Identifying test files does not execute tests or confirm their results.
* AI-generated summaries may be incomplete or incorrect.
* GitHub API rate limits may restrict unauthenticated requests.
* Large pull requests may be summarized using only a subset of the available diff context.

PRNarrator is a reviewer-assistance tool, not a replacement for human code review, automated testing, or dedicated security analysis.
