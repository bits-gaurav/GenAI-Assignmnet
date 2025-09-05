from fastapi import FastAPI, Request, HTTPException
import httpx
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pipeline Monitor", version="1.0.0")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

@app.get("/")
def home():
    config_status = {
        "slack_configured": bool(SLACK_WEBHOOK_URL),
        "github_token_configured": bool(GITHUB_TOKEN),
        "environment": ENVIRONMENT
    }
    return {
        "message": "Pipeline Monitor Running 🚀", 
        "status": "healthy",
        "config": config_status
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "pipeline-monitor"}

@app.post("/github-webhook")
async def github_webhook(request: Request):
    try:
        # Log the incoming request
        logger.info("Received GitHub webhook request")
        
        payload = await request.json()
        logger.info(f"Webhook payload keys: {list(payload.keys())}")
        
        # Handle different GitHub webhook events
        if "workflow_run" in payload:
            return await handle_workflow_run_event(payload)
        elif "action" in payload and payload.get("action") in ["completed", "failed"]:
            return await handle_workflow_job_event(payload)
        else:
            logger.warning(f"Unhandled webhook event type: {payload.keys()}")
            return {"status": "ignored", "reason": "unsupported_event_type"}
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

async def handle_workflow_run_event(payload: Dict[Any, Any]):
    """Handle workflow_run events from GitHub"""
    workflow_run = payload.get("workflow_run", {})
    workflow_status = workflow_run.get("conclusion", "unknown")
    workflow_name = workflow_run.get("name", "Unknown Workflow")
    repo = payload.get("repository", {}).get("full_name", "unknown")
    actor = payload.get("sender", {}).get("login", "unknown")
    branch = workflow_run.get("head_branch", "unknown")
    
    logger.info(f"Workflow run event: status={workflow_status}, repo={repo}, actor={actor}, branch={branch}")

    if workflow_status == "failure":
        logger.info("Processing pipeline failure...")
        message = f"🚨 **Pipeline Failure Alert**\n" \
                 f"• Repository: `{repo}`\n" \
                 f"• Workflow: `{workflow_name}`\n" \
                 f"• Branch: `{branch}`\n" \
                 f"• Triggered by: `{actor}`\n" \
                 f"• Status: `{workflow_status}`"
        
        slack_success = await send_slack_alert(message)
        rollback_success = await trigger_rollback(repo)
        
        return {
            "status": "processed", 
            "workflow_status": workflow_status,
            "notifications": {
                "slack_sent": slack_success,
                "rollback_triggered": rollback_success
            }
        }
    
    return {"status": "ok", "workflow_status": workflow_status, "processed": False}

async def handle_workflow_job_event(payload: Dict[Any, Any]):
    """Handle workflow job events (alternative event type)"""
    action = payload.get("action")
    workflow_job = payload.get("workflow_job", {})
    conclusion = workflow_job.get("conclusion")
    
    if action == "completed" and conclusion == "failure":
        repo = payload.get("repository", {}).get("full_name", "unknown")
        actor = payload.get("sender", {}).get("login", "unknown")
        job_name = workflow_job.get("name", "Unknown Job")
        
        message = f"🚨 **Job Failure Alert**\n" \
                 f"• Repository: `{repo}`\n" \
                 f"• Job: `{job_name}`\n" \
                 f"• Triggered by: `{actor}`\n" \
                 f"• Status: `{conclusion}`"
        
        slack_success = await send_slack_alert(message)
        return {"status": "processed", "job_status": conclusion, "slack_sent": slack_success}
    
    return {"status": "ok", "action": action, "conclusion": conclusion}

async def send_slack_alert(message: str) -> bool:
    """Send alert to Slack webhook. Returns True if successful, False otherwise."""
    try:
        if not SLACK_WEBHOOK_URL:
            logger.warning("SLACK_WEBHOOK_URL not configured - cannot send alert")
            return False
        
        payload = {
            "text": message,
            "username": "Pipeline Monitor",
            "icon_emoji": ":warning:"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SLACK_WEBHOOK_URL, 
                json=payload, 
                timeout=10.0,
                headers={"Content-Type": "application/json"}
            )
            
        if response.status_code == 200:
            logger.info("Slack alert sent successfully")
            return True
        else:
            logger.error(f"Failed to send Slack alert. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except httpx.TimeoutException:
        logger.error("Timeout while sending Slack alert")
        return False
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False

async def trigger_rollback(repo: str) -> bool:
    """Trigger rollback via GitHub repository dispatch. Returns True if successful, False otherwise."""
    try:
        if not GITHUB_TOKEN:
            logger.warning("GITHUB_TOKEN not configured - skipping rollback")
            return False
            
        async with httpx.AsyncClient() as client:
            url = f"https://api.github.com/repos/{repo}/dispatches"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            data = {
                "event_type": "rollback",
                "client_payload": {
                    "reason": "pipeline_failure",
                    "timestamp": str(int(__import__('time').time()))
                }
            }
            
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            
        if response.status_code == 204:
            logger.info(f"Rollback triggered successfully for {repo}")
            return True
        else:
            logger.error(f"Failed to trigger rollback. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except httpx.TimeoutException:
        logger.error("Timeout while triggering rollback")
        return False
    except Exception as e:
        logger.error(f"Failed to trigger rollback: {e}")
        return False
