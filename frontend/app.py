import os

import httpx
import streamlit as st


API_URL = os.getenv("PRNARRATOR_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="PRNarrator",
    layout="wide",
)

st.title("PRNarrator")
st.caption("AI-assisted GitHub pull request analysis and review")

st.markdown(
    "Analyze pull request changes, inspect heuristic risk signals, "
    "identify test-related files, and generate a reviewer-focused report."
)

with st.form("analyze_pr_form"):
    pr_url = st.text_input(
        "GitHub pull request URL",
        placeholder="https://github.com/owner/repo/pull/123",
    )
    submitted = st.form_submit_button(
        "Analyze pull request",
        type="primary",
    )

if submitted:
    if not pr_url.strip():
        st.warning("Enter a GitHub pull request URL.")
    else:
        try:
            with st.spinner(
                "Fetching changes and generating the AI review..."
            ):
                response = httpx.post(
                    f"{API_URL}/analyze",
                    json={"pr_url": pr_url.strip()},
                    timeout=300.0,
                )

            if response.is_error:
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text

                st.error(f"Analysis failed: {detail}")

            else:
                result = response.json()
                report = result["analysis"]
                pr = report["pull_request"]
                diff = report["diff_summary"]
                risk = report["risk_analysis"]
                tests = report["test_analysis"]

                st.success("Analysis completed.")

                st.subheader(pr["title"])
                st.markdown(f"[Open pull request]({pr['url']})")
                st.caption(
                    f"Author: {pr['author']} | State: {pr['state']} | "
                    f"Branch: {pr['head_branch']} → {pr['base_branch']}"
                )

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Files changed", diff["changed_file_count"])
                col2.metric("Additions", diff["total_additions"])
                col3.metric("Deletions", diff["total_deletions"])
                col4.metric("Heuristic risk", risk["risk_level"].upper())

                st.subheader("AI-generated review")
                st.markdown(result["ai_review"])

                st.subheader("Risk findings")
                st.caption(risk.get("note", "Heuristic estimate only."))

                if risk["findings"]:
                    for index, finding in enumerate(risk["findings"], start=1):
                        with st.expander(
                            f"{index}. {finding['category'].replace('_', ' ').title()}"
                        ):
                            if finding.get("file"):
                                st.write(f"**File:** `{finding['file']}`")
                            st.write(finding["reason"])
                else:
                    st.info("No risk signals were detected by the current heuristics.")

                st.subheader("Test coverage signals")
                st.write(tests["message"])

                if tests["test_files"]:
                    st.write("**Detected test-related files**")
                    for filename in tests["test_files"]:
                        st.markdown(f"- `{filename}`")

                st.subheader("Changed files")

                if diff["files"]:
                    for file in diff["files"]:
                        with st.expander(file["filename"]):
                            st.write(f"**Status:** {file['status']}")
                            st.write(f"**Additions:** {file['additions']}")
                            st.write(f"**Deletions:** {file['deletions']}")

                            patch = file.get("patch", "")
                            if patch:
                                st.code(patch, language="diff")
                            else:
                                st.caption(
                                    "GitHub did not provide a patch for this file."
                                )
                else:
                    st.info("No changed-file details are available.")

                with st.expander("View structured analysis data"):
                    st.json(report)

        except httpx.ConnectError:
            st.error(
                "Cannot connect to the API. Start the FastAPI server "
                "in another terminal and try again."
            )
        except httpx.TimeoutException:
            st.error(
                "The request timed out. Check the API terminal and "
                "whether Ollama is responding."
            )
        except (KeyError, ValueError) as exc:
            st.error(f"Unexpected API response: {exc}")
        except httpx.HTTPError as exc:
            st.error(f"Request failed: {exc}")

st.divider()
st.caption(
    "Risk scores are heuristic signals, not proof of vulnerabilities. "
    "Detected test files do not establish that tests pass."
)
