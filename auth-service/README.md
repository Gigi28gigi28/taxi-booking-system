# Auth Microservice

Django REST API for authentication and user management with JWT tokens.

## Features

- Email-based authentication
- JWT access/refresh tokens with rotation and blacklisting
- Role-based access control (passager, chauffeur)
- Rate limiting on login endpoints
- Password validation and change
- Profile management
- CORS support for frontend integration

## Requirements

- Python 3.8+
- Django 5.2+
- PostgreSQL (production) / SQLite (development)
- djangorestframework
- djangorestframework-simplejwt
- django-cors-headers

## Installation

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

## Environment Variables

SECRET_KEY - Django secret key
DEBUG - True/False
ALLOWED_HOSTS - Comma-separated hosts
DB_ENGINE - Database engine (default: sqlite3)
DB_NAME - Database name
DB_USER - Database user
DB_PASSWORD - Database password
DB_HOST - Database host
DB_PORT - Database port
JWT_ACCESS_TOKEN_LIFETIME - Minutes (default: 15)
JWT_REFRESH_TOKEN_LIFETIME - Minutes (default: 10080)
CORS_ALLOWED_ORIGINS - Comma-separated origins
SECURE_SSL_REDIRECT - True/False for production

## API Endpoints

POST /accounts/api/register/ - Register new user (passager by default)
POST /accounts/api/login/ - Login and get tokens
POST /accounts/api/logout/ - Blacklist refresh token
GET /accounts/api/me/ - Get current user info
PATCH /accounts/api/profile/update/ - Update profile
POST /accounts/api/change-password/ - Change password
POST /accounts/api/chauffeur/login/ - Chauffeur-specific login

POST /api/token/refresh/ - Refresh access token
POST /api/token/verify/ - Verify token validity

## Rate Limiting

Login endpoints: 5 attempts per 15 minutes per IP/email
Failed attempts result in 15-minute block

## Security

- HTTPS enforced in production
- HSTS headers enabled
- XSS and clickjacking protection
- CSRF protection
- Secure cookie flags in production
- Password validators (length, common passwords, similarity, numeric)

## User Roles

passager - Default role for registered users
chauffeur - Driver role (must be set manually or via admin)
superuser - Full admin access

## Development

python manage.py runserver

Access admin panel at /admin/

## Production Notes

- Set DEBUG=False
- Use PostgreSQL
- Configure proper SECRET_KEY
- Enable SSL redirect
- Set secure CORS origins
- Use environment variables for all sensitive config
