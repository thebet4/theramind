# TheraMind API Collection

Bruno API testing collection for TheraMind backend.

## Quick Start

1. Open Bruno and load this collection
2. Select **"Development"** environment
3. Run `Auth/Login` to authenticate
4. Token is auto-captured - all requests now work

## Environment Variables

Set in Bruno's environment:

```
host = http://localhost:8000
access_token = (auto-set by Login)
```

## Collection Structure

```
Bruno/
├── Auth/          # Signup, Login, Refresh
├── Therapist/     # Profile management
├── Patients/      # Patient CRUD
└── Sessions/      # Audio upload & processing
```

## Session Upload Flow

1. **Generate Upload URL** → `Sessions/1-Generate-Upload-URL`
2. **Upload audio to S3** → Use returned presigned URL (via curl/fetch)
3. **Create Session** → `Sessions/2-Create-Session`
4. **Check Status** → `Sessions/4-Get-Session` (poll until `completed`)

## Troubleshooting

- **401 Unauthorized?** → Re-run `Auth/Login`
- **Backend not running?** → `cd backend && uvicorn app.main:app --reload`

## Complete API Documentation

📖 **Full API reference with schemas and examples:**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

💡 Use Bruno for testing, Swagger for reference.
