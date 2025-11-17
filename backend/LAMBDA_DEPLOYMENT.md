# TheraMind Lambda Worker Deployment

## Overview

The TheraMind worker processes therapy session audio files using AWS Lambda. It transcribes audio, generates summaries, and anonymizes personal information.

## Architecture

The worker is now **unified with the backend codebase** to share configuration and reduce duplication:

```
backend/
├── app/
│   ├── core/
│   │   └── config.py              # Unified configuration
│   ├── services/
│   │   └── processing/            # Worker services
│   │       ├── transcription.py   # Whisper API
│   │       ├── summarizer.py      # GPT-4o-mini
│   │       ├── anonymizer.py      # PII removal
│   │       ├── aws_clients.py     # S3/SQS clients
│   │       ├── database.py        # Database operations
│   │       └── processor.py       # Main orchestrator
│   └── workers/
│       └── lambda_handler.py      # Lambda entry point
├── build_lambda.sh                # Build deployment package
└── deploy_lambda.sh               # Deploy to AWS
```

## Environment Variables

All environment variables are managed through `app/core/config.py`:

### Required for Lambda:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for Whisper and GPT
- `S3_BUCKET_NAME` - S3 bucket for audio files
- `AWS_REGION` - AWS region (default: us-east-1)

### Optional:
- `LOG_LEVEL` - Logging level (default: INFO)

## Deployment

### Prerequisites

1. Docker installed (for building Lambda package)
2. AWS CLI configured
3. Environment variables set in `.env` file

### Build and Deploy

```bash
cd backend

./build_lambda.sh
./deploy_lambda.sh
```

### Manual Deployment

Build only:
```bash
./build_lambda.sh
```

Then manually upload:
```bash
aws lambda update-function-code \
  --function-name theramind-processor \
  --zip-file fileb://lambda_function.zip \
  --region us-east-1
```

## Configuration

### Lambda Settings
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 900 seconds (15 minutes)
- **Handler**: `app.workers.lambda_handler.lambda_handler`

### IAM Permissions

The Lambda function needs:
- S3: GetObject, DeleteObject, HeadObject
- SQS: ReceiveMessage, DeleteMessage, GetQueueAttributes, ChangeMessageVisibility
- CloudWatch Logs: CreateLogGroup, CreateLogStream, PutLogEvents

## Monitoring

View logs:
```bash
aws logs tail /aws/lambda/theramind-processor --follow
```

## Development

### Local Testing

```python
cd backend
python -m app.workers.lambda_handler
```

### Testing Individual Components

```python
from app.services.processing import TranscriptionService, SummarizerService

transcriber = TranscriptionService()
summarizer = SummarizerService()
```

## Benefits of Unified Structure

1. **Single Configuration**: Environment variables managed in one place
2. **Code Reuse**: Backend and worker share the same services
3. **Easier Testing**: Services can be tested independently
4. **Better Maintainability**: One codebase, one source of truth
5. **Shared Dependencies**: Single requirements.txt for all components

