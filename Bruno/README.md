# TheraMind API Collection

Complete API documentation and testing collection for the TheraMind backend.

## 🚀 Quick Start

1. **Set Environment**: Select "Development" environment (default: `http://0.0.0.0:8000`)
2. **Sign Up**: Run `Auth/signup` to create a therapist account
3. **Login**: Run `Auth/Login` to authenticate (token auto-saved)
4. **Make Requests**: All protected endpoints will automatically use your token

## 📁 Collection Structure

### Auth

- **Signup** - Create new therapist account
- **Login** - Authenticate and get access token (auto-captured)

### Therapist

- **Get Current Therapist** - Retrieve your profile
- **Update Profile** - Update account information
- **Delete Account** - Permanently delete account ⚠️

### Patients

- **Create Patient** - Add new patient to your practice
- **List (Paginated)** - View patients with pagination and filters

## 🔐 Authentication

### Automatic Token Management

This collection features **automatic token handling**:

1. Run `Auth/Login` → Token automatically captured and stored
2. All protected endpoints → Token automatically injected in headers
3. Token expires → Re-run Login to refresh

### Token Details

- **Format**: JWT Bearer token
- **Expiration**: 60 minutes
- **Storage**: Environment variable `access_token`
- **Usage**: Automatic via `Authorization: Bearer {{access_token}}`

## 🌐 Environment Variables

| Variable       | Description              | Default               |
| -------------- | ------------------------ | --------------------- |
| `host`         | API base URL             | `http://0.0.0.0:8000` |
| `access_token` | JWT token (auto-managed) | (set by Login)        |

## 📖 Request Documentation

Each request includes comprehensive documentation with:

- **Purpose**: What the endpoint does
- **Authentication**: Requirements and token usage
- **Request Format**: Body parameters and validation rules
- **Response Examples**: Success and error responses
- **Error Codes**: Common status codes and meanings
- **Notes**: Important considerations and best practices

Click on any request and view the "Docs" tab for detailed information.

## 🔍 Pagination & Filtering

The `Patients/List (Paginated)` endpoint supports:

**Pagination:**

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10, max: 100)

**Filters:**

- `identifier` - Search by patient ID (partial match)
- `consent_given` - Filter by consent status
- `created_after` - Filter by creation date (from)
- `created_before` - Filter by creation date (to)

**Response includes:**

- `total` - Total number of patients
- `page` - Current page
- `page_size` - Items per page
- `total_pages` - Total pages available
- `patients` - Array of patient objects

## 💡 Tips

- **401 Errors**: Token expired → Re-run Login
- **400 Errors**: Check request body format
- **422 Errors**: Validation failed → Check field requirements
- **Commented Parameters**: Lines with `~` prefix are commented → Remove to activate

## 🛠️ Development

### Local Backend Server

Ensure your backend server is running:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Flow

1. **Create Account**: Run `Auth/signup`
2. **Authenticate**: Run `Auth/Login` (token auto-saved)
3. **Verify Auth**: Run `Therapist/Get Current Therapist`
4. **Create Patient**: Run `Patients/Create Patient`
5. **List Patients**: Run `Patients/List (Paginated)`

## 📝 Notes

- All requests include example data - update before running
- Sensitive data (passwords, emails) in examples should be changed
- Patient identifiers are unique per therapist (not globally unique)
- Soft delete is used (data isn't permanently removed immediately)
- Date formats: ISO 8601 (e.g., `2024-01-15T00:00:00` or `2024-01-15`)

## 🆘 Troubleshooting

**Token not working?**

- Check if token is set: View environment variables
- Re-run Login to get fresh token
- Verify "Development" environment is selected

**Request failing?**

- Check backend server is running
- Verify request body format matches docs
- Check response for specific error message

**Can't see documentation?**

- Click on a request
- Open the "Docs" tab in the right panel
- Markdown documentation will be displayed
