# TheraMind - Worker (AWS Lambda)

Serverless worker for processing audio sessions.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp ../.env.example .env
# Edit .env with your AWS and OpenAI credentials

# Test locally
python handler.py

# Build deployment package
./build.sh

# Deploy to AWS Lambda
aws lambda update-function-code \
  --function-name theramind-processor \
  --zip-file fileb://function.zip
```

## 📁 Project Structure

```
worker/
├── handler.py              # Lambda entry point
├── processor.py            # Main processing logic
├── transcription.py        # Whisper integration
├── summarizer.py           # GPT integration
├── anonymizer.py           # PII removal
├── aws_clients.py          # S3, SQS clients
├── requirements.txt        # Dependencies
├── build.sh               # Build script
└── Dockerfile             # For local testing
```

## 🔄 Processing Flow

```python
def lambda_handler(event, context):
    """
    1. Parse SQS message
    2. Download audio from S3
    3. Transcribe with Whisper
    4. Generate summary with GPT-4o-mini
    5. Anonymize PII
    6. Save to database
    7. Delete audio from S3
    8. Send notification
    """
```

## 🧪 Testing Locally

```bash
# Using Docker
docker build -t theramind-worker .
docker run -e AWS_ACCESS_KEY_ID=xxx theramind-worker

# Using SAM CLI
sam local invoke -e events/test-event.json

# Unit tests
pytest tests/
```

## 📦 Dependencies

- `boto3` - AWS SDK
- `openai` - OpenAI API
- `psycopg2-binary` - PostgreSQL
- `pydantic` - Validation
- `python-dotenv` - Environment variables

## 🚀 Deployment

### Using AWS CLI

```bash
# Package
./build.sh

# Create Lambda function
aws lambda create-function \
  --function-name theramind-processor \
  --runtime python3.11 \
  --role arn:aws:iam::123456789:role/lambda-role \
  --handler handler.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 900 \
  --memory-size 1024

# Update function
aws lambda update-function-code \
  --function-name theramind-processor \
  --zip-file fileb://function.zip
```

### Using Terraform

```bash
cd ../terraform
terraform init
terraform plan
terraform apply
```

## ⚙️ Configuration

### Lambda Settings

- **Runtime:** Python 3.11
- **Memory:** 1024 MB
- **Timeout:** 15 minutes
- **Concurrent executions:** 10 (MVP)

### Environment Variables

Set in AWS Lambda console or via Terraform:
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `S3_BUCKET_NAME`
- `SENTRY_DSN`

### SQS Trigger

- **Batch size:** 1 (process one at a time)
- **Visibility timeout:** 15 minutes
- **Max retries:** 3

## 📊 Monitoring

```python
# CloudWatch Logs
aws logs tail /aws/lambda/theramind-processor --follow

# Metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=theramind-processor \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

## 🔍 Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with specific session
from handler import lambda_handler

event = {
    "Records": [{
        "body": '{"session_id": "uuid-here"}'
    }]
}

result = lambda_handler(event, None)
print(result)
```

## 🚨 Error Handling

- **Transient errors:** Retry with exponential backoff (3x)
- **Permanent errors:** Log to `processing_errors` table
- **Critical errors:** Alert via Sentry
- **SQS DLQ:** Messages that fail 3x go to Dead Letter Queue

