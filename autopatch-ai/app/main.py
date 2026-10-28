import os
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from github import Github
from dotenv import load_dotenv
from app.agent import analyze_code_diff

load_dotenv()

app = FastAPI(title="AutoPatch AI Agent")

gh_client = Github(os.getenv("GITHUB_TOKEN"))


def process_pull_request(payload: dict):
    """
    Background worker to fetch PR diffs, execute Nebius AI analysis,
    post PR review comments, and commit code patches automatically.
    """
    repo_full_name = payload["repository"]["full_name"]
    pr_number = payload["number"]

    repo = gh_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    # Get modified files in PR
    files = pr.get_files()

    for file in files:
        if file.status in ["removed"]:
            continue

        filename = file.filename
        patch = file.patch

        if not patch:
            continue

        print(f"[+] Processing file: {filename} in PR #{pr_number}")

        # Analyze using NVIDIA Nemotron on Nebius
        try:
            analysis = analyze_code_diff(filename, patch)
        except Exception as e:
            print(f"[-] Error calling Nebius API: {e}")
            continue

        if analysis.get("has_issues"):
            # 1. Post analysis comment on PR
            comment_body = (
                f"### 🛡️ AutoPatch AI Security Review\n\n"
                f"**Summary:** {analysis.get('summary')}\n\n"
                f"{analysis.get('review_comment')}\n\n"
                f"*Powered by NVIDIA Nemotron on Nebius Cloud Token Factory*"
            )
            pr.create_issue_comment(comment_body)

            # 2. Automatically push fixed code back to the PR branch
            fixed_code = analysis.get("fixed_content")
            if fixed_code:
                branch_name = pr.head.ref
                try:
                    existing_file = repo.get_contents(filename, ref=branch_name)
                    repo.update_file(
                        path=filename,
                        message=f"style(autopatch): automated fix for {filename}",
                        content=fixed_code,
                        sha=existing_file.sha,
                        branch=branch_name
                    )
                    print(f"[+] Successfully pushed commit fix to branch `{branch_name}` for {filename}")
                except Exception as commit_err:
                    print(f"[-] Failed to update file on branch: {commit_err}")


@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    if event_type == "pull_request":
        action = payload.get("action")
        # Trigger on PR opening or push updates
        if action in ["opened", "synchronize"]:
            background_tasks.add_task(process_pull_request, payload)
            return {"status": "queued", "action": action}

    return {"status": "ignored", "event": event_type}


@app.get("/health")
def health_check():
    return {"status": "online", "engine": "Nebius Token Factory (NVIDIA Nemotron)"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
