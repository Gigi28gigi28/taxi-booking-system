# Auth Service

JWT-based authentication and user management microservice for the TaxiBook platform.

##  Overview

The Auth Service handles:
- User registration (passengers and drivers)
- JWT token generation and validation
- User authentication and authorization
- Role-based access control
- Token blacklisting on logout
- Rate limiting for security
- Automatic Consul registration

##  Architecture

```
┌─────────────────────────────────────┐
│         Auth Service API            │
├─────────────────────────────────────┤
│  • User Registration                │
│  • Login (Passenger/Driver)         │
│  • Token Management (JWT)           │
│  • Token Verification               │
│  • Profile Management               │
│  • Password Change                  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Django Models               │
│  • Custom User (Compte)             │
│  • Role: Passenger/Chauffeur        │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      SQLite/PostgreSQL DB           │
└─────────────────────────────────────┘
```

##  Features

- **JWT Authentication**: Secure token-based authentication
- **Role Management**: Passenger and Driver roles
- **Token Blacklisting**: Invalidate tokens on logout
- **Rate Limiting**: Prevent brute force attacks
- **Service Discovery**: Auto-registration with Consul
- **CORS Handling**: Cross-origin request support
- **Password Validation**: Secure password requirements
- **Email Validation**: Unique email addresses

## Tech Stack

- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.15.2
- **Authentication**: djangorestframework-simplejwt 5.3.1
- **CORS**: django-cors-headers 4.3.1
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Service Registry**: python-consul 1.1.0

## Installation

### Prerequisites
- Python 3.10+
- pip
- virtualenv

### Setup

1. **Navigate to service directory**
```bash
cd auth-service
```

2. **Create virtual environment**
```bash
python -m venv .venv
```

3. **Activate virtual environment**

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**

Create `.env` file (optional):
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Consul Configuration
CONSUL_HOST=localhost
CONSUL_PORT=8500
SERVICE_NAME=auth-service
SERVICE_PORT=8000
SERVICE_HOST=127.0.0.1
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

8. **Run server**
```bash
python manage.py runserver 0.0.0.0:8000
```

## API Endpoints

### Public Endpoints (No Authentication)

#### Register Passenger
```http
POST /accounts/api/register/
Content-Type: application/json

{
  "email": "passenger@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "nom": "Doe",
  "prenom": "John"
}

Response: 201 Created
{
  "user": {
    "id": 1,
    "email": "passenger@example.com",
    "nom": "Doe",
    "prenom": "John",
    "role": "passager"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1...",
    "access": "eyJ0eXAiOiJKV1..."
  }
}
```

#### Login (Passenger)
```http
POST /accounts/api/login/
Content-Type: application/json

{
  "email": "passenger@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "user": {
    "id": 1,
    "email": "passenger@example.com",
    "nom": "Doe",
    "prenom": "John",
    "role": "passager"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1...",
    "access": "eyJ0eXAiOiJKV1..."
  }
}
```

#### Login (Driver)
```http
POST /accounts/api/chauffeur/login/
Content-Type: application/json

{
  "email": "driver@example.com",
  "password": "SecurePass123!"
}
```

#### Token Verification
```http
POST /accounts/api/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1..."
}

Response: 200 OK
{
  "id": 1,
  "email": "passenger@example.com",
  "role": "passager"
}
```

### Protected Endpoints (Requires JWT)

#### Get Current User
```http
GET /accounts/api/me/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "id": 1,
  "email": "passenger@example.com",
  "nom": "Doe",
  "prenom": "John",
  "role": "passager"
}
```

#### Update Profile
```http
PATCH /accounts/api/profile/update/
Authorization: Bearer eyJ0eXAiOiJKV1...
Content-Type: application/json

{
  "nom": "Smith",
  "prenom": "Jane"
}
```

#### Change Password
```http
POST /accounts/api/change-password/
Authorization: Bearer eyJ0eXAiOiJKV1...
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

#### Logout
```http
POST /accounts/api/logout/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1..."
}

Response: 200 OK
{
  "detail": "Successfully logged out."
}
```

### JWT Token Endpoints

#### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1..."
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1..."
}
```

#### Verify Token
```http
POST /api/token/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1..."
}
```

## Security Features

### Rate Limiting
Login endpoints are rate-limited to prevent brute force attacks:
- **Max Attempts**: 5 attempts
- **Window**: 15 minutes
- **Block Time**: 15 minutes after exceeding limit

Configuration in `settings.py`:
```python
LOGIN_RATE_LIMIT = {
    'MAX_ATTEMPTS': 5,
    'WINDOW_MINUTES': 15,
    'BLOCK_MINUTES': 15,
}
```

### Password Requirements
- Minimum 8 characters
- Cannot be similar to user attributes
- Cannot be commonly used password
- Cannot be entirely numeric

### JWT Configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

## Database Models

### Compte (User Model)
```python
class Compte(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=150, blank=True)
    prenom = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=30, 
        choices=[('passager', 'Passager'), ('chauffeur', 'Chauffeur')],
        default='passager'
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
```

## Service Discovery

The service automatically registers with Consul on startup:

```python
# consul_utils.py
def register_service():
    service_data = {
        "ID": "auth-service-8000",
        "Name": "auth-service",
        "Address": "127.0.0.1",
        "Port": 8000,
        "Tags": [
            "traefik.enable=true",
            "traefik.http.routers.auth-service.rule=PathPrefix(`/accounts/`) || PathPrefix(`/api/token/`)",
        ],
        "Check": {
            "HTTP": "http://127.0.0.1:8000/admin/login/",
            "Interval": "10s",
            "Timeout": "3s"
        }
    }
    # Register with Consul...
```

## Testing

### Manual Testing

1. **Register a user**
```bash
curl -X POST http://localhost:8000/accounts/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "password2": "Test123!",
    "nom": "Test",
    "prenom": "User"
  }'
```

2. **Login**
```bash
curl -X POST http://localhost:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

3. **Access protected endpoint**
```bash
curl -X GET http://localhost:8000/accounts/api/me/ \
  -H "Authorization: Bearer <your-token>"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Auto-generated |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |
| `DB_ENGINE` | Database engine | `sqlite3` |
| `CONSUL_HOST` | Consul host | `localhost` |
| `CONSUL_PORT` | Consul port | `8500` |
| `SERVICE_NAME` | Service name | `auth-service` |
| `SERVICE_PORT` | Service port | `8000` |
| `SERVICE_HOST` | Service host | `127.0.0.1` |


##  Related Services

- [Ride Service](../ride-service/README.md)
- [Frontend](../ui/README.md)
- [Root Documentation](../README.md)
