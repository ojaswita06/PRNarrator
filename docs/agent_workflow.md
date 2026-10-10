# PRNarrator Agent Workflow

## Purpose

PRNarrator uses LangGraph to generate a reviewer-focused explanation of a GitHub pull request. The workflow combines deterministic analysis results with a local language model.

## Workflow Stages

### 1. Receive the Pull Request

The user submits a GitHub pull request URL through the Streamlit frontend. The FastAPI backend validates the request format before processing it.

### 2. Retrieve Pull Request Data

The GitHub client retrieves available pull request metadata and changed-file information, including file names, change counts, and patch excerpts.

If GitHub cannot provide the required data, the application reports an error rather than inventing repository information.

### 3. Run Deterministic Analysis

The analysis service creates a structured report using three categories of analysis:

* **Diff analysis:** Summarizes changed files, additions, deletions, and file types.
* **Risk analysis:** Calculates heuristic signals from change size and file characteristics.
* **Test analysis:** Identifies files that appear related to tests.

These steps provide evidence for the AI review. They do not execute the project's tests or establish that the code is secure.

### 4. Build the Review Context

The `build_context()` function in `app/agent/nodes.py` extracts the relevant pull request metadata, diff summary, risk analysis, and test analysis.

To keep the prompt manageable, it limits the number of included files and the length of each patch excerpt.

### 5. Execute the LangGraph Workflow

The graph in `app/agent/graph.py` contains one node:

`START → generate_review → END`

The `generate_review` node receives the analysis report through the graph state and calls the local Ollama model.

This is a single-node LangGraph workflow, not a multi-agent system.

### 6. Generate the AI Review

The node combines the structured context with the review instructions in `app/agent/prompts.py`. The configured Ollama model generates a natural-language report intended to help a developer review the pull request.

The report includes sections such as:

* PR Overview
* What Changed
* Risk Assessment
* Test Coverage Signals
* Reviewer Checklist

The review should remain grounded in the available evidence. Recommendations must not be treated as proof that a defect or vulnerability exists.

### 7. Return and Display Results

The FastAPI endpoint returns the deterministic analysis and AI-generated review. The Streamlit frontend presents the results to the user.

If analysis or generation fails, the API returns an error response instead of claiming that the review succeeded.

## State and Data Flow

The LangGraph state contains the analysis report and the generated review.

* **Input:** Structured pull request analysis report.
* **Processing:** Context preparation and Ollama inference.
* **Output:** Generated reviewer-focused text.

## Failure Handling

Potential failure conditions include GitHub API errors, rate limits, unavailable Ollama services, missing models, and model-generation errors.

The application surfaces API errors and logs internal processing failures. Users should verify that GitHub is reachable and the configured Ollama model is available before retrying failed analyses.

## Human Review

PRNarrator assists code review but does not replace it. Developers should inspect the actual diff, validate important claims, run appropriate tests, and independently assess security-sensitive changes.
