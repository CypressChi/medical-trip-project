# Medical Trip Backend - Quick Start Guide

## System Status
✅ **All systems operational and tested**

### Versions
- Django: 4.2.27
- Django REST Framework: 3.16.1
- djangorestframework-simplejwt: 5.5.1
- Python: 3.13.5

## Running the Server

### 1. Activate Virtual Environment
```powershell
# Windows
.\.venv\Scripts\Activate.ps1

# Or from project root
cd backend
..\.venv\Scripts\python.exe manage.py runserver
```

### 2. Start Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

Server will run at: `http://localhost:8000`

## API Endpoints - Quick Reference

### Authentication (No Auth Required)
```bash
# 1. Register new user
POST /api/auth/register/
{
  "username": "john_doe",
  "password": "SecurePass123!",
  "email": "john@example.com",
  "phone": "+16471234567",
  "language_preference": "en"
}

Response:
{
  "user": {...},
  "access": "eyJ...",
  "refresh": "eyJ..."
}

# 2. Login
POST /api/auth/login/
{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response:
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}

# 3. Refresh Token
POST /api/auth/refresh/
{
  "refresh": "eyJ..."
}

Response:
{
  "access": "eyJ..."
}
```

### Protected Endpoints (Requires JWT)

Add header: `Authorization: Bearer <access_token>`

```bash
# Get user's profile
GET /api/profiles/<id>/

# List user's consultations
GET /api/consultations/

# Create consultation
POST /api/consultations/
{
  "doctor": 1,
  "symptoms": "fever and headache"
}

# Get specific consultation
GET /api/consultations/<id>/

# List all doctors
GET /api/doctors/

# Get doctor detail
GET /api/doctors/<id>/

# AI Triage (symptom analysis)
POST /api/triage/
{
  "symptoms": "fever headache dizziness"
}

Response:
{
  "suggested_department": "Neurology",
  "confidence": "high",
  "description": "..."
}
```

## Testing with curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@1234",
    "email": "test@example.com",
    "phone": "+16471234567",
    "language_preference": "en"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@1234"
  }'

# Access protected resource
curl -X GET http://localhost:8000/api/consultations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Refresh token
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

## Testing with Postman

1. Create environment variable:
   - `access_token`: (will be filled after login)
   - `refresh_token`: (will be filled after login)

2. Collection:
   - POST Register: `/api/auth/register/`
   - POST Login: `/api/auth/login/` → Save tokens to environment
   - GET Profile: `/api/profiles/{profile_id}/` with Bearer token
   - GET Consultations: `/api/consultations/` with Bearer token
   - POST AI Triage: `/api/triage/` with Bearer token

## Features Verified

✅ User registration with auto UserProfile creation
✅ JWT authentication (1hr access, 7day refresh)
✅ Token refresh mechanism
✅ Permission system (data ownership enforcement)
✅ CORS enabled for frontend access
✅ Mock AI triage (keyword-based)
✅ Doctor management
✅ Consultation booking
✅ Admin interface

## Database

Default database: `db.sqlite3`

Reset database:
```bash
# Delete old database
rm db.sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

Access admin at: `http://localhost:8000/admin`

## Troubleshooting

### Port already in use
```bash
# Use different port
python manage.py runserver 0.0.0.0:8001
```

### ALLOWED_HOSTS error
Edit `medical_trip/settings.py`:
```python
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'your-domain.com']
```

### JWT Token expired
Get new token using refresh token endpoint:
```bash
POST /api/auth/refresh/
```

### Permission denied (403)
- Ensure JWT token is valid
- Check data ownership (users can only access own data)
- Admins bypass all permission checks

## Next Steps

1. **Production Setup**
   - Change SECRET_KEY
   - Set DEBUG = False
   - Configure proper ALLOWED_HOSTS
   - Use PostgreSQL instead of SQLite
   - Set up environment variables

2. **Real AI Integration**
   - Replace `_mock_ai_analysis()` in views.py
   - Integrate OpenAI or Baidu Wenxin API
   - Add AI model selection

3. **Additional Features**
   - Email notifications
   - Payment integration (Stripe/Alipay)
   - File upload (medical documents)
   - Appointment scheduling
   - Video consultation

## Support

For issues or questions, check:
- Django docs: https://docs.djangoproject.com/
- DRF docs: https://www.django-rest-framework.org/
- JWT docs: https://django-rest-framework-simplejwt.readthedocs.io/
