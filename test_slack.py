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
        print("💡 Create a .env file with: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK")
        return
    
    message = "🧪 **Test Alert from GenAI Assignment Pipeline Monitor**\n" \
             "• This is a test message to verify Slack integration\n" \
             "• If you see this, your webhook is working correctly! ✅"
    
    payload = {
        "text": message,
        "username": "Pipeline Monitor Test",
        "icon_emoji": ":test_tube:"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                slack_webhook_url, 
                json=payload,
                timeout=10.0,
                headers={"Content-Type": "application/json"}
            )
            
        if response.status_code == 200:
            print("✅ Slack alert sent successfully!")
            print(f"📱 Check your Slack channel for the test message")
        else:
            print(f"❌ Failed to send Slack alert. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except httpx.TimeoutException:
        print("❌ Timeout while sending Slack alert")
    except Exception as e:
        print(f"❌ Error sending Slack alert: {e}")

async def test_fastapi_health():
    """Test if the FastAPI service is running and healthy"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            
        if response.status_code == 200:
            print("✅ FastAPI service is healthy")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ FastAPI service health check failed. Status: {response.status_code}")
            
    except httpx.ConnectError:
        print("❌ Cannot connect to FastAPI service at localhost:8000")
        print("💡 Start the service with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error checking FastAPI health: {e}")

async def main():
    """Run all tests"""
    print("🔧 Testing Slack Integration and FastAPI Service\n")
    
    print("1. Testing FastAPI Health...")
    await test_fastapi_health()
    print()
    
    print("2. Testing Slack Alert...")
    await test_slack_alert()
    print()
    
    print("✨ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
