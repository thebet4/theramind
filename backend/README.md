# TheraMind Backend

FastAPI backend with unified worker services.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env

alembic upgrade head
uvicorn app.main:app --reload
```

## Structure

```
backend/
├── app/
│   ├── core/              # Config, auth, database
│   ├── api/               # API endpoints
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          
│   │   └── processing/    # Worker services (shared)
│   └── workers/           # Lambda handler
├── build_lambda.sh
├── deploy_lambda.sh
└── requirements.txt
```

## API Documentation

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Bruno Collection: `/Bruno/`

## Lambda Worker

See [LAMBDA_DEPLOYMENT.md](LAMBDA_DEPLOYMENT.md) for deployment instructions.

