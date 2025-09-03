import asyncio
import httpx
import json

async def test_webhook_endpoint():
    """Test the GitHub webhook endpoint with a simulated failure payload"""
    
    # Simulated GitHub webhook payload for a failed workflow
    test_payload = {
        "workflow_run": {
            "conclusion": "failure",
            "name": "CI Pipeline",
            "head_branch": "main"
        },
        "repository": {
            "full_name": "bits-gaurav/GenAI-Assignment"
        },
        "sender": {
            "login": "bits-gaurav"
        }
    }
    
    webhook_url = "http://localhost:8000/github-webhook"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=test_payload,
                timeout=10.0
            )
            
        if response.status_code == 200:
            print("✅ Webhook endpoint responded successfully!")
            print(f"Response: {response.json()}")
            print("🔔 This should have triggered a Slack alert if your webhook URL is valid")
        else:
            print(f"❌ Webhook endpoint failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except httpx.ConnectError:
        print("❌ Could not connect to the FastAPI app.")
        print("Make sure your app is running with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook_endpoint())
