# Ride Service

Ride management and notification microservice for the TaxiBook platform, handling ride requests, matching, and real-time notifications.

##  Overview

The Ride Service manages:
- Ride creation and lifecycle management
- Driver-passenger matching workflow
- Real-time notification system
- Ride status tracking
- Integration with message queue (RabbitMQ)
- JWT token validation via Auth Service
- Automatic Consul registration

##  Architecture

```
┌──────────────────────────────────────────┐
│         Ride Service API                 │
├──────────────────────────────────────────┤
│  • Ride CRUD Operations                  │
│  • Status Management                     │
│  • Notification System                   │
│  • Driver Actions (Accept/Reject)        │
│  • Passenger Actions (Request/Cancel)    │
└────────┬─────────────────────────────────┘
         │
         ├──────────────────┬─────────────────┐
         ▼                  ▼                 ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│   Django DB     │  │  RabbitMQ    │  │ Auth Service │
│  (SQLite/PG)    │  │  (Messages)  │  │ (Token Validation)│
└─────────────────┘  └──────┬───────┘  └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │Matcher Worker│
                     └──────────────┘
```

## Features

-  **Ride Management**: Complete CRUD operations
-  **State Machine**: Proper ride status transitions
-  **RabbitMQ Integration**: Event-driven architecture
-  **Real-time Notifications**: Polling-based notification system
-  **JWT Middleware**: Validates tokens with Auth Service
-  **Internal API**: Microservice-to-microservice communication
-  **Service Discovery**: Auto-registration with Consul
-  **Role-based Access**: Separate views for passengers and drivers

## Tech Stack

- **Framework**: Django 5.2.7
- **API**: Django REST Framework
- **Message Queue**: pika (RabbitMQ client)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Service Registry**: python-consul 1.1.0
- **HTTP Client**: requests

##  Installation

### Prerequisites
- Python 3.10+
- RabbitMQ server running
- Auth Service running (for token validation)

### Setup

1. **Navigate to service directory**
```bash
cd ride-service
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

Create `.env` file:
```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=*

# Database (PostgreSQL for production)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Auth Service URL
AUTH_VERIFY_URL=http://localhost:8000/accounts/api/verify/

# Consul Configuration
CONSUL_HOST=localhost
CONSUL_PORT=8500
SERVICE_NAME=ride-service
SERVICE_PORT=8001
SERVICE_HOST=127.0.0.1
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Run server**
```bash
python manage.py runserver 0.0.0.0:8001
```

## API Endpoints

### Passenger Endpoints (Requires JWT)

#### Create Ride Request
```http
POST /api/rides/
Authorization: Bearer eyJ0eXAiOiJKV1...
Content-Type: application/json

{
  "origin": "123 Main Street, Downtown",
  "destination": "456 Oak Avenue, Uptown"
}

Response: 201 Created
{
  "id": 1,
  "passenger": 5,
  "driver": null,
  "origin": "123 Main Street, Downtown",
  "destination": "456 Oak Avenue, Uptown",
  "status": "requested",
  "price": null,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:00:00Z"
}
```

#### Get My Rides
```http
GET /api/rides/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
[
  {
    "id": 1,
    "passenger": 5,
    "driver": 10,
    "origin": "123 Main Street",
    "destination": "456 Oak Avenue",
    "status": "accepted",
    "price": 10.00,
    "created_at": "2025-12-24T10:00:00Z",
    "updated_at": "2025-12-24T10:05:00Z"
  }
]
```

#### Cancel Ride
```http
POST /api/rides/{ride_id}/cancel/
Authorization: Bearer eyJ0eXAiOiJKV1...
Content-Type: application/json

{
  "reason": "Changed plans"
}

Response: 200 OK
{
  "id": 1,
  "status": "cancelled",
  ...
}
```

#### Get Ride Status (Polling)
```http
GET /api/rides/{ride_id}/status/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "ride": {
    "id": 1,
    "status": "accepted",
    "driver": 10,
    ...
  },
  "recent_notifications": [
    {
      "id": 1,
      "title": "Driver Accepted Your Ride",
      "message": "A driver has accepted your ride! They will pick you up soon!",
      "is_read": false,
      "created_at": "2025-12-24T10:05:00Z"
    }
  ]
}
```

### Driver Endpoints (Requires JWT)

#### Get Available Rides
```http
GET /api/rides/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
[
  {
    "id": 1,
    "passenger": 5,
    "driver": 10,
    "origin": "123 Main Street",
    "destination": "456 Oak Avenue",
    "status": "offered",
    "price": null,
    "created_at": "2025-12-24T10:00:00Z",
    "updated_at": "2025-12-24T10:02:00Z"
  }
]
```

#### Accept Ride
```http
POST /api/rides/{ride_id}/accept/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "id": 1,
  "status": "accepted",
  "driver": 10,
  ...
}
```

#### Reject Ride
```http
POST /api/rides/{ride_id}/reject/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "detail": "Ride rejected, searching for another driver"
}
```

#### Complete Ride
```http
POST /api/rides/{ride_id}/complete/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "id": 1,
  "status": "completed",
  "price": 10.00,
  ...
}
```

### Notification Endpoints

#### Get All Notifications
```http
GET /api/notifications/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "count": 5,
  "unread_count": 2,
  "notifications": [
    {
      "id": 1,
      "user_id": 5,
      "ride": 1,
      "notification_type": "ride_accepted",
      "title": "Driver Accepted Your Ride",
      "message": "A driver has accepted your ride!",
      "is_read": false,
      "created_at": "2025-12-24T10:05:00Z"
    }
  ]
}
```

#### Get Unread Notifications
```http
GET /api/notifications/unread/
Authorization: Bearer eyJ0eXAiOiJKV1...
```

#### Mark as Read
```http
POST /api/notifications/{notification_id}/mark_as_read/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "id": 1,
  "is_read": true,
  ...
}
```

#### Mark All as Read
```http
POST /api/notifications/mark_all_as_read/
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "detail": "Marked 5 notifications as read"
}
```

#### Poll for New Notifications
```http
GET /api/notifications/poll/?since=2025-12-24T10:00:00Z
Authorization: Bearer eyJ0eXAiOiJKV1...

Response: 200 OK
{
  "count": 2,
  "notifications": [...],
  "timestamp": "2025-12-24T10:10:00Z"
}
```

### Internal API (No Authentication - Microservice Communication)

#### Assign Driver (Matcher Worker)
```http
POST /api/internal/rides/{ride_id}/assign-driver/
Content-Type: application/json

{
  "driver_id": 10
}

Response: 200 OK
{
  "success": true,
  "ride": {...},
  "message": "Driver 10 assigned to ride 1"
}
```

#### Get Ride (Internal)
```http
GET /api/internal/rides/{ride_id}/
```

#### Update Status (Internal)
```http
POST /api/internal/rides/{ride_id}/update-status/
Content-Type: application/json

{
  "status": "accepted"
}
```

## Ride Status Flow

```
requested → offered → accepted → completed
    ↓          ↓          ↓
  cancelled ← cancelled ← cancelled
```

**Status Transitions:**
1. **requested**: Passenger creates ride, published to RabbitMQ
2. **offered**: Matcher assigns driver, notifies driver
3. **accepted**: Driver accepts ride, notifies passenger
4. **completed**: Driver marks as complete, calculates price
5. **cancelled**: Either party cancels (notifies other party)

## RabbitMQ Events

### Published Events

#### ride.requested
```json
{
  "ride_id": 1,
  "passenger_id": 5,
  "origin": "123 Main Street",
  "destination": "456 Oak Avenue",
  "event": "ride_requested"
}
```

#### ride.accepted
```json
{
  "ride_id": 1,
  "driver_id": 10,
  "passenger_id": 5,
  "event": "ride_accepted"
}
```

#### ride.completed
```json
{
  "ride_id": 1,
  "driver_id": 10,
  "passenger_id": 5,
  "price": "10.00",
  "event": "ride_completed"
}
```

#### ride.cancelled
```json
{
  "ride_id": 1,
  "cancelled_by": 5,
  "reason": "Changed plans",
  "event": "ride_cancelled"
}
```

#### notifications
```json
{
  "user_id": 5,
  "notification_type": "ride_accepted",
  "title": "Driver Accepted Your Ride",
  "message": "A driver has accepted your ride!",
  "ride_id": 1,
  "event": "notification"
}
```

## Database Models

### Ride Model
```python
class Ride(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_OFFERED = "offered"
    STATUS_ACCEPTED = "accepted"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    passenger = models.IntegerField()  # From auth-service
    driver = models.IntegerField(null=True, blank=True)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default=STATUS_REQUESTED)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Notification Model
```python
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ride_requested', 'Ride Requested'),
        ('ride_offered', 'Ride Offered'),
        ('ride_accepted', 'Ride Accepted'),
        ('ride_rejected', 'Ride Rejected'),
        ('ride_completed', 'Ride Completed'),
        ('ride_cancelled', 'Ride Cancelled'),
    ]

    user_id = models.IntegerField()
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Authentication Middleware

The service uses custom JWT verification middleware:

```python
# auth_middleware.py
def jwt_verification_middleware(get_response):
    def middleware(request):
        # Skip admin, static, and internal API
        # Extract JWT from Authorization header
        # Verify with Auth Service
        # Attach user_data to request
        return get_response(request)
    return middleware
```

**How it works:**
1. Extracts JWT from `Authorization: Bearer <token>` header
2. Calls Auth Service `/accounts/api/verify/` endpoint
3. Attaches `user_id`, `user_email`, `user_role` to request
4. Returns 401 if token is invalid

## Service Discovery

Auto-registers with Consul:

```python
service_data = {
    "ID": "ride-service-8001",
    "Name": "ride-service",
    "Address": "127.0.0.1",
    "Port": 8001,
    "Tags": [
        "traefik.enable=true",
        "traefik.http.routers.ride-service.rule=PathPrefix(`/api/rides`) || PathPrefix(`/api/notifications`)",
    ],
    "Check": {
        "HTTP": "http://127.0.0.1:8001/admin/login/",
        "Interval": "10s"
    }
}
```

## Testing

### Create and Track Ride Flow

```bash
# 1. Register and login as passenger
TOKEN=$(curl -s -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"passenger@test.com","password":"Test123!"}' \
  | jq -r '.access')

# 2. Request a ride
RIDE_ID=$(curl -s -X POST http://localhost:8001/api/rides/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"origin":"Main St","destination":"Oak Ave"}' \
  | jq -r '.id')

# 3. Check ride status
curl -X GET http://localhost:8001/api/rides/$RIDE_ID/status/ \
  -H "Authorization: Bearer $TOKEN"

# 4. Check notifications
curl -X GET http://localhost:8001/api/notifications/ \
  -H "Authorization: Bearer $TOKEN"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Auto-generated |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `*` |
| `DB_ENGINE` | Database engine | `sqlite3` |
| `RABBITMQ_URL` | RabbitMQ connection URL | `amqp://guest:guest@localhost:5672/` |
| `AUTH_VERIFY_URL` | Auth service verify endpoint | `http://localhost:8000/accounts/api/verify/` |
| `CONSUL_HOST` | Consul host | `localhost` |
| `SERVICE_PORT` | Service port | `8001` |


##  Related Services

- [Auth Service](../auth-service/README.md)
- [Matcher Worker](../matcher-worker/README.md)
- [Frontend](../ui/README.md)
- [Root Documentation](../README.md)
