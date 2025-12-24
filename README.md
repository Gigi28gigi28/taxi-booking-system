# TaxiBook - Microservices Architecture

A distributed taxi booking system built with microservices architecture, featuring service discovery, API gateway, message queuing, and multi-PC deployment capabilities.

##  Architecture Overview

```
┌─────────────┐
│   Frontend  │ (React - Vite)
│  Port 3000  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Traefik API Gateway             │
│            Port 8080                    │
│  (Load Balancing & Routing)             │
└───────┬────────────────┬────────────────┘
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Auth-Service │  │ Ride-Service │
│  Port 8000   │  │  Port 8001   │
│  (Django)    │  │  (Django)    │
└──────┬───────┘  └──────┬───────┘
       │                 │
       │                 ▼
       │          ┌──────────────┐
       │          │  RabbitMQ    │
       │          │  Port 5672   │
       │          └──────┬───────┘
       │                 │
       │                 ▼
       │          ┌──────────────┐
       │          │Matcher Worker│
       │          │ (Python)     │
       │          └──────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           Consul Service Registry       │
│              Port 8500                  │
│       (Service Discovery)               │
└─────────────────────────────────────────┘
```

## 🌟 Key Features

- **Microservices Architecture**: Independently deployable services
- **Service Discovery**: Consul for automatic service registration and discovery
- **API Gateway**: Traefik for routing, load balancing, and CORS handling
- **Message Queue**: RabbitMQ for asynchronous communication
- **Real-time Notifications**: Polling-based notification system
- **JWT Authentication**: Secure token-based authentication
- **Role-based Access Control**: Separate interfaces for passengers and drivers
- **Multi-PC Deployment**: Distributed deployment across multiple machines

##  Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| **Auth Service** | 8000 | Django + DRF | User authentication & authorization |
| **Ride Service** | 8001 | Django + DRF | Ride management & notifications |
| **Matcher Worker** | - | Python | Ride matching & driver assignment |
| **Notification Consumer** | - | Python | Notification processing |
| **Frontend** | 3000 | React + Vite | User interface |
| **Traefik Gateway** | 8080 | Traefik | API Gateway & load balancer |
| **Consul** | 8500 | HashiCorp Consul | Service registry |
| **RabbitMQ** | 5672, 15672 | RabbitMQ | Message broker |

## Multi-PC Deployment

### Team Setup (4 PCs)

Our deployment was distributed across **4 machines** with the following configuration:

#### **PC1 - Leader (Project Lead Machine)** 

-  Consul Leader (Service Registry)
-  Traefik Gateway (API Gateway)
-  Frontend (React UI)
- **Role**: Central coordination point for service discovery and routing

#### **PC2 - Backend Services**

-  Auth-Service (Port 8000)
-  RabbitMQ (Ports 5672, 15672)

#### **PC3 - Backend Services**

-  Ride-Service (Port 8001)

#### **PC4 - Workers**
-  Matcher Worker
- Notification Consumer

### Network Configuration

All machines must be on the **same local network** and can reach each other. Update IP addresses in configuration files:

**Frontend (`ui/src/services/api.js`):**
```javascript
export const AUTH_URL = 'http://10.70.95.95:8080';  // Points to Traefik on PC1
export const RIDE_URL = 'http://10.70.95.95:8080';
```

**Traefik (`traefik-dynamic.yml`):**
```yaml
services:
  auth-service:
    loadBalancer:
      servers:
        - url: "http://10.70.95.87:8000"  # PC2
  
  ride-service:
    loadBalancer:
      servers:
        - url: "http://10.70.95.49:8001"  # PC3
```

**Consul (`consul-config.json`):**
```json
{
  "bind_addr": "10.70.95.95",      // PC1 IP
  "advertise_addr": "10.70.95.95",
  "client_addr": "0.0.0.0"
}
```

##  Prerequisites

- Python 3.10+
- Node.js 18+
- Consul (HashiCorp)
- Traefik 2.x
- RabbitMQ
- Git

##  Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd taxibook-microservices
```

### 2. Setup Services

Refer to individual service README files:
- [Auth Service README](./auth-service/README.md)
- [Ride Service README](./ride-service/README.md)
- [Matcher Worker README](./matcher-worker/README.md)
- [Frontend README](./ui/README.md)

##  Quick Start (Single PC Development)

### Start Infrastructure Services
```bash
# 1. Start Consul
consul agent -dev -config-file=consul-config.json

# 2. Start RabbitMQ (if not running as service)
# Already running as Windows service usually

# 3. Start Traefik
traefik --configFile=traefik.yml
```

### Start Application Services
```bash
# 4. Auth Service
cd auth-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 5. Ride Service (new terminal)
cd ride-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001

# 6. Matcher Worker (new terminal)
cd matcher-worker
pip install -r requirements.txt
python matcher_worker.py

# 7. Notification Consumer (new terminal)
cd matcher-worker
python notification_consumer.py

# 8. Frontend (new terminal)
cd ui
npm install
npm run dev
```

### Or use the automated script:
```bash
start-all.bat
```

##  Testing

### Test API via Traefik Gateway
```bash
# Register a passenger
curl -X POST http://localhost:8080/accounts/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger@test.com",
    "password": "Test123!",
    "password2": "Test123!",
    "nom": "Doe",
    "prenom": "John"
  }'

# Login
curl -X POST http://localhost:8080/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger@test.com",
    "password": "Test123!"
  }'

# Request a ride (use token from login)
curl -X POST http://localhost:8080/api/rides/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "origin": "123 Main St",
    "destination": "456 Oak Ave"
  }'
```

### Automated Full System Test
```bash
python test-full-system.py
```

##  Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Gateway | http://localhost:8080 |
| Traefik Dashboard | http://localhost:8082 |
| Consul UI | http://localhost:8500 |
| RabbitMQ Management | http://localhost:15672 |
| Auth Service (Direct) | http://localhost:8000 |
| Ride Service (Direct) | http://localhost:8001 |

##  Default Credentials

**RabbitMQ:**
- Username: `guest`
- Password: `guest`

**Django Admin:**
Create superuser: `python manage.py createsuperuser`

## Key Concepts

### Service Discovery with Consul
Services automatically register themselves with Consul on startup. Traefik discovers services via Consul and routes traffic accordingly.

### API Gateway Pattern
Traefik acts as a single entry point, handling:
- Load balancing across service instances
- CORS configuration
- Request routing based on path
- Health checks

### Event-Driven Architecture
RabbitMQ enables asynchronous communication:
1. Passenger requests ride → Published to `ride.requested` queue
2. Matcher worker processes → Assigns driver → Published to `ride.offer` queue
3. Notification consumer → Sends notifications to users

### JWT Authentication
- Auth service issues JWT tokens
- Ride service validates tokens via internal API
- Middleware attaches user data to requests

##  Development

### Adding a New Service

1. **Create Service**
```bash
django-admin startproject myservice
```

2. **Register with Consul**
Add to `apps.py`:
```python
from .consul_utils import register_service
register_service()
```

3. **Configure Traefik**
Update `traefik-dynamic.yml`:
```yaml
myservice:
  loadBalancer:
    servers:
      - url: "http://localhost:8002"
```

4. **Add Routing**
```yaml
my-router:
  rule: "PathPrefix(`/api/myservice/`)"
  service: myservice
```

##  Troubleshooting

### Service Not Discoverable
```bash
# Check Consul registration
curl http://localhost:8500/v1/catalog/services

# Check service health
curl http://localhost:8500/v1/health/service/auth-service
```

### Traefik Not Routing
```bash
# Check Traefik logs for routing errors
# Visit: http://localhost:8082 (Traefik Dashboard)
```

### RabbitMQ Connection Issues
```bash
# Check RabbitMQ status
rabbitmqctl status

# Check queues
rabbitmqctl list_queues
```

### CORS Errors
Ensure Traefik CORS middleware is configured correctly in `traefik-dynamic.yml`.

##  Team & Contributions

**Project Team: 4 Members**
- **PC1 (Leader)**: Infrastructure setup, Consul, Traefik, Frontend
- **PC2**: Auth Service, RabbitMQ setup
- **PC3**: Ride Service
- **PC4**: Worker services

This project demonstrates distributed system design and multi-machine deployment coordination.



## 📧 Contact

For questions or support, please open an issue in the repository.
