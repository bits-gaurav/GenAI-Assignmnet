from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TOKEN = os.getenv("TOKEN")

@app.get("/")
def home():
    return {"message": "Pipeline Monitor Running 🚀"}

@app.post("/github-webhook")
async def github_webhook(request: Request):
    try:
        payload = await request.json()
        workflow_status = payload.get("workflow_run", {}).get("conclusion", "unknown")
        repo = payload.get("repository", {}).get("full_name", "unknown")
        actor = payload.get("sender", {}).get("login", "unknown")

        print(f"Received webhook: status={workflow_status}, repo={repo}, actor={actor}")

        if workflow_status == "failure":
            print("Triggering failure notifications...")
            await send_slack_alert(f"❌ CI/CD pipeline failed in {repo} by {actor}")
            await trigger_rollback(repo)
            print("Notifications sent successfully")

        return {"status": "ok", "processed": workflow_status == "failure"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

async def send_slack_alert(message: str):
    try:
        if not SLACK_WEBHOOK_URL:
            print("Warning: SLACK_WEBHOOK_URL not configured")
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=10.0)
            print(f"Slack alert sent: {response.status_code}")
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")

async def trigger_rollback(repo: str):
    try:
        if not TOKEN:
            print("Warning: TOKEN not configured, skipping rollback")
            return
            
        async with httpx.AsyncClient() as client:
            url = f"https://api.github.com/repos/{repo}/dispatches"
            headers = {"Authorization": f"token {TOKEN}"}
            data = {"event_type": "rollback"}
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            print(f"Rollback triggered: {response.status_code}")
    except Exception as e:
        print(f"Failed to trigger rollback: {e}")
