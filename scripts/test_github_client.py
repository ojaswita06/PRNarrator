
from app.github.client import GitHubClient, GitHubClientError


def main():
    client = GitHubClient()
    url = "https://github.com/fastapi/fastapi/pull/1"

    try:
        pr = client.get_pull_request(url)

        print("GitHub connection successful!")
        print("Title:", pr["title"])
        print("Author:", pr["author"])
        print("State:", pr["state"])
        print("Changed files:", pr["changed_file_count"])
        print("Files retrieved:", len(pr["files"]))

        if pr["files"]:
            print("First changed file:", pr["files"][0]["filename"])

    except (GitHubClientError, ValueError) as exc:
        print("GitHub test failed:", exc)


if __name__ == "__main__":
    main()