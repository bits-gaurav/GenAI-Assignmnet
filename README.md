# GenAI Assignment - Pipeline Monitor with Slack Alerts

A FastAPI-based monitoring service that sends Slack notifications when GitHub CI/CD pipelines fail, with automatic rollback capabilities.

## 🚀 Features

- **Slack Notifications**: Instant alerts when pipelines fail
- **GitHub Integration**: Webhook endpoint for GitHub Actions
- **Automatic Rollback**: Triggers rollback workflows on failure
- **Health Monitoring**: Built-in health checks and status endpoints
- **Comprehensive Logging**: Detailed logging for debugging

## 📋 Prerequisites

- Python 3.11+
- Slack workspace with webhook permissions
- GitHub repository with Actions enabled
- Optional: GitHub Personal Access Token for rollback functionality

## 🛠️ Setup Instructions

### 1. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure your `.env` file:
   ```env
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
   GITHUB_TOKEN=your_github_personal_access_token_here
   ENVIRONMENT=production
   ```

### 2. Slack Webhook Setup

1. Go to your Slack workspace settings
2. Navigate to **Apps** → **Incoming Webhooks**
3. Create a new webhook for your desired channel
4. Copy the webhook URL to your `.env` file

### 3. GitHub Secrets Configuration

Add these secrets to your GitHub repository:

- `SLACK_WEBHOOK_URL`: Your Slack webhook URL
- `WEBHOOK_URL`: Your deployed FastAPI service URL (optional)

**Path**: Repository Settings → Secrets and variables → Actions

### 4. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Docker Deployment (Optional)

```bash
# Build the image
docker build -t pipeline-monitor .

# Run the container
docker run -p 8000:8000 --env-file .env pipeline-monitor
```

## 🧪 Testing

### Test Slack Integration
```bash
python test_slack.py
```

### Test Webhook Endpoint
```bash
python test_webhook.py
```

### Manual Testing
1. Start the FastAPI service: `uvicorn app.main:app --reload`
2. Check health: `curl http://localhost:8000/health`
3. View configuration: `curl http://localhost:8000/`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status and configuration |
| `/health` | GET | Health check endpoint |
| `/github-webhook` | POST | GitHub webhook receiver |

## 🔧 How It Works

### GitHub Actions Integration

The CI pipeline (`.github/workflows/ci.yml`) includes two notification methods:

1. **Direct Slack Notification**: Uses curl to send alerts directly to Slack
2. **Webhook Notification**: Sends payload to your FastAPI service (backup method)

### Failure Detection

The system detects failures through:
- GitHub Actions `if: failure()` condition
- Webhook payload analysis for `conclusion: "failure"`
- Support for both `workflow_run` and `workflow_job` events

### Notification Flow

```
GitHub Action Fails → Slack Alert + Webhook → FastAPI Service → Rollback Trigger
```

## 🐛 Troubleshooting

### Common Issues

**Slack alerts not working:**
- Verify `SLACK_WEBHOOK_URL` in `.env` file
- Check Slack webhook is active in workspace settings
- Test with `python test_slack.py`

**Webhook not receiving data:**
- Ensure FastAPI service is publicly accessible
- Verify `WEBHOOK_URL` secret in GitHub repository
- Check service logs for incoming requests

**GitHub Actions failing:**
- Review workflow logs in GitHub Actions tab
- Verify secrets are properly configured
- Check if webhook URL is reachable from GitHub

### Debug Commands

```bash
# Check service status
curl http://localhost:8000/

# Test webhook manually
curl -X POST http://localhost:8000/github-webhook \
  -H "Content-Type: application/json" \
  -d '{"workflow_run":{"conclusion":"failure"},"repository":{"full_name":"test/repo"}}'

# View service logs
uvicorn app.main:app --reload --log-level debug
```

## 📊 Monitoring

The service provides detailed logging for:
- Incoming webhook requests
- Slack notification attempts
- Rollback trigger attempts
- Configuration validation

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use GitHub secrets for sensitive data
- Validate webhook payloads in production
- Consider implementing webhook signature verification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is part of a GenAI assignment and is for educational purposes.