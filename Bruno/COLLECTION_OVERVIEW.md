# API Collection Overview

## Endpoints Summary

### Authentication Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/signup` | POST | ❌ No | Create therapist account |
| `/api/v1/login` | POST | ❌ No | Authenticate and get token |

### Therapist Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/me` | GET | ✅ Yes | Get current therapist profile |
| `/api/v1/me` | PUT | ✅ Yes | Update therapist profile |
| `/api/v1/me` | DELETE | ✅ Yes | Delete therapist account |

### Patient Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/patients` | POST | ✅ Yes | Create new patient |
| `/api/v1/patients` | GET | ✅ Yes | List patients (paginated) |

## Response Status Codes

### Success Codes

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Request successful, no content returned

### Client Error Codes

- **400 Bad Request** - Invalid request data or business logic error
- **401 Unauthorized** - Missing, invalid, or expired authentication token
- **404 Not Found** - Resource doesn't exist
- **422 Unprocessable Entity** - Validation errors in request data

### Server Error Codes

- **500 Internal Server Error** - Unexpected server error

## Data Models

### Therapist

```json
{
  "id": "uuid",
  "email": "string",
  "full_name": "string",
  "professional_license": "string"
}
```

### Patient

```json
{
  "id": "uuid",
  "identifier": "string",
  "date_of_birth": "datetime|null",
  "consent_given": "boolean",
  "created_at": "datetime"
}
```

### Login Response

```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer",
  "therapist": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "professional_license": "string"
  }
}
```

### Paginated Response

```json
{
  "total": "integer",
  "page": "integer",
  "page_size": "integer",
  "total_pages": "integer",
  "patients": [Patient]
}
```

## Authentication Flow

```
1. Sign Up (POST /api/v1/signup)
   ↓
2. Login (POST /api/v1/login)
   ↓ (returns access_token)
3. Use token in header: Authorization: Bearer {token}
   ↓
4. Access protected endpoints
   ↓
5. Token expires after 60 minutes
   ↓ (re-login)
6. Repeat from step 2
```

## Validation Rules

### Therapist Sign Up

- **email**: Valid email format, must be unique
- **full_name**: Required, non-empty string
- **professional_license**: Required, non-empty string
- **password**: 8-72 bytes, must match confirm_password

### Patient Creation

- **identifier**: Required, unique per therapist
- **date_of_birth**: Optional, ISO 8601 datetime format

### Therapist Update

- All fields optional
- **email**: If provided, must be valid and unique
- **full_name**: If provided, must be non-empty
- **professional_license**: If provided, must be non-empty

## Security Notes

- Passwords hashed with bcrypt before storage
- JWT tokens expire after 60 minutes
- Bearer token authentication for protected endpoints
- Each therapist can only access their own data
- Patient identifiers scoped per therapist

## Rate Limiting

Currently no rate limiting implemented. Consider implementing in production.

## Versioning

Current API version: **v1**

All endpoints prefixed with `/api/v1/`

