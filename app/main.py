from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@app.get("/")
def home():
    return {"message": "Pipeline Monitor Running 🚀"}

@app.post("/github-webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    workflow_status = payload.get("workflow_run", {}).get("conclusion", "unknown")
    repo = payload.get("repository", {}).get("full_name", "unknown")
    actor = payload.get("sender", {}).get("login", "unknown")

    if workflow_status == "failure":
        await send_slack_alert(f"❌ CI/CD pipeline failed in {repo} by {actor}")
        await trigger_rollback(repo)

    return {"status": "ok"}

async def send_slack_alert(message: str):
    async with httpx.AsyncClient() as client:
        await client.post(SLACK_WEBHOOK_URL, json={"text": message})

async def trigger_rollback(repo: str):
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/repos/{repo}/dispatches"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        data = {"event_type": "rollback"}
        await client.post(url, headers=headers, json=data)
