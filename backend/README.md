# TheraMind - Backend API

FastAPI backend for TheraMind platform.

## 🚀 Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp ../.env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── dependencies.py      # DI dependencies
│   │
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication
│   │   ├── sessions.py      # Session management
│   │   ├── patients.py      # Patient CRUD
│   │   └── therapists.py    # Therapist profile
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── therapist.py
│   │   ├── patient.py
│   │   ├── session.py
│   │   └── audit_log.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── session.py
│   │   └── patient.py
│   │
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── audio_service.py
│   │   ├── queue_service.py
│   │   └── auth_service.py
│   │
│   ├── core/                # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py      # Auth helpers
│   │   ├── database.py      # DB connection
│   │   └── aws.py           # AWS clients
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/                   # Tests
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_sessions.py
│   └── conftest.py
│
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
│
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Dev dependencies
├── pyproject.toml          # Project metadata
└── .env.example            # Environment variables
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py -v
```

## 📝 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Security Notes

- Never commit `.env` files
- Use environment variables for all secrets
- Enable HTTPS in production
- Implement rate limiting
- Validate all inputs with Pydantic

