# 🧠 TheraMind

> AI-powered session management platform for independent therapists

TheraMind is a SaaS platform that simplifies patient management and automates therapy session summaries using AI. Upload audio recordings of sessions and receive structured, privacy-focused summaries highlighting key discussion points, emotions, and action items.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## ✨ Features

- **🎙️ Audio Processing** - Upload session recordings (up to 50 minutes) with automatic transcription via OpenAI Whisper
- **🤖 AI-Powered Summaries** - Generate structured summaries using GPT-4o-mini with complete session context
- **🔒 Privacy-First** - Zero-storage policy: audio files are permanently deleted after processing
- **👥 Patient Management** - Organize and track therapy sessions with an intuitive dashboard
- **⚡ Real-time Updates** - WebSocket notifications when processing completes
- **🌐 GDPR/LGPD Compliant** - Built-in data protection and anonymization features

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │────────▶│   FastAPI    │────────▶│  SQS Queue  │
│  (Frontend) │  HTTPS  │  (Backend)   │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │                         │
      │                        ▼                         ▼
      │                  ┌──────────────┐         ┌─────────────┐
      │                  │  PostgreSQL  │         │   Worker    │
      │                  │  (Supabase)  │◀────────│  (Lambda)   │
      │                  └──────────────┘         └─────────────┘
      │                                                  │
      ▼                                                  ▼
┌─────────────┐                                  ┌─────────────┐
│     S3      │◀─────────────────────────────────│   OpenAI    │
│  (Storage)  │     Deleted after processing     │  Whisper +  │
└─────────────┘                                  │   GPT-4o    │
                                                 └─────────────┘
```

## 🚀 Tech Stack

### Frontend

- **React 19** + **TypeScript** + **Vite**
- **TailwindCSS 4** for styling
- **React Router** for navigation
- **Framer Motion** for animations
- **i18next** for internationalization

### Backend

- **FastAPI** + **Python 3.11+**
- **PostgreSQL** (Supabase)
- **SQLAlchemy** + **Alembic** for database management
- **Supabase Auth** for authentication
- **AWS Lambda** for async processing
- **AWS S3** for temporary storage
- **AWS SQS** for job queuing

### AI Services

- **OpenAI Whisper** - Audio transcription ($0.006/min)
- **OpenAI GPT-4o-mini** - Summary generation ($0.15/1M tokens)

## 📦 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or Supabase account)
- AWS Account (for S3, SQS, Lambda)
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### API Testing

Use the included Bruno collection for API testing:

```bash
# Open Bruno and import the collection from /Bruno
```

## 🔒 Security & Privacy

- **Zero-Storage Policy** - Audio files deleted within 2 hours of processing
- **Automatic Anonymization** - PII removed from AI-generated summaries
- **End-to-End Encryption** - TLS 1.3 for all connections
- **Row-Level Security** - Therapists only access their own data
- **Rate Limiting** - Protection against abuse
- **GDPR/LGPD Compliant** - Built-in data subject rights

## 📊 Project Structure

```
TheraMind/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config, auth, database
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── workers/     # Lambda handlers
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   └── package.json
├── Bruno/               # API collection
├── docs/                # Documentation
└── tests/               # Test suites
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper and GPT-4 APIs
- Supabase for database and authentication
- The open-source community

---

**Note:** This is an MVP in active development. For production deployment, refer to the comprehensive documentation in `/docs`.
