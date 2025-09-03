import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_slack_alert():
    """Test sending a Slack alert directly"""
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not slack_webhook_url:
        print("❌ SLACK_WEBHOOK_URL not found in environment variables")
        return
    
    message = "🧪 Test alert from GenAI Assignment pipeline monitor"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                slack_webhook_url, 
                json={"text": message},
                timeout=10.0
            )
            
        if response.status_code == 200:
            print("✅ Slack alert sent successfully!")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Failed to send Slack alert. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending Slack alert: {e}")

if __name__ == "__main__":
    asyncio.run(test_slack_alert())
