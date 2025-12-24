# Matcher Worker & Notification Consumer

Background workers for ride matching and notification processing in the TaxiBook platform.

##  Overview

This directory contains two Python workers that handle asynchronous tasks:

1. **Matcher Worker** (`matcher_worker.py`): Matches ride requests with available drivers
2. **Notification Consumer** (`notification_consumer.py`): Processes and sends notifications to users

Both workers consume messages from RabbitMQ queues and interact with the Ride Service via internal APIs.

##  Architecture

```
┌─────────────────────────────────────────┐
│           RabbitMQ Broker               │
│                                         │
│  Queues:                                │
│  • ride.requested                       │
│  • ride.offer                           │
│  • notifications                        │
└────┬────────────────────────┬───────────┘
     │                        │
     ▼                        ▼
┌──────────────────┐  ┌──────────────────┐
│ Matcher Worker   │  │ Notification     │
│                  │  │ Consumer         │
│ • Find drivers   │  │ • Send emails    │
│ • Assign rides   │  │ • Send SMS       │
│ • Publish offers │  │ • Send push      │
└────────┬─────────┘  └──────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     Ride Service Internal API            │
│  POST /api/internal/rides/{id}/          │
│       assign-driver/                     │
└──────────────────────────────────────────┘
```

##  Features

### Matcher Worker
-  **Listens to**: `ride.requested` queue
-  **Driver Matching**: Simulated driver availability check
-  **Ride Assignment**: Updates ride with assigned driver via internal API
-  **Event Publishing**: Publishes `ride.offer` event for drivers
-  **Notification Publishing**: Publishes notifications for drivers
-  **Error Handling**: Automatic retry on failures

### Notification Consumer
-  **Listens to**: `notifications` queue
-  **Multi-channel**: Email, SMS, Push notifications (simulated)
-  **User Targeting**: Routes notifications to specific users
-  **Error Handling**: Graceful failure handling
-  **Logging**: Comprehensive activity logging

##  Tech Stack

- **Language**: Python 3.10+
- **Message Queue**: pika (RabbitMQ client)
- **HTTP Client**: requests
- **Environment**: python-dotenv

##  Installation

### Prerequisites
- Python 3.10+
- RabbitMQ server running
- Ride Service running (for internal API calls)

### Setup

1. **Navigate to worker directory**
```bash
cd matcher-worker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create `.env` file:
```env
# RabbitMQ Configuration
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Ride Service API
RIDE_SERVICE_URL=http://localhost:8001/api/rides

# Internal API (no JWT required)
INTERNAL_API_URL=http://localhost:8001/api/internal
```

4. **Run workers**

Terminal 1 - Matcher Worker:
```bash
python matcher_worker.py
```

Terminal 2 - Notification Consumer:
```bash
python notification_consumer.py
```

## Matcher Worker Details

### How It Works

1. **Listens** to `ride.requested` queue
2. **Receives** ride request message:
```json
{
  "ride_id": 1,
  "passenger_id": 5,
  "origin": "123 Main Street",
  "destination": "456 Oak Avenue",
  "event": "ride_requested"
}
```

3. **Finds** available driver (simulated):
   - In production: Query driver database
   - Check driver location vs pickup
   - Consider ratings, acceptance rate
   - Use ML for optimal matching
   - Currently: Randomly selects from fake driver pool

4. **Assigns** driver via internal API:
```http
POST /api/internal/rides/1/assign-driver/
Content-Type: application/json

{
  "driver_id": 102
}
```

5. **Publishes** two events:

   a. **ride.offer** (to driver):
   ```json
   {
     "ride_id": 1,
     "driver_id": 102,
     "passenger_id": 5,
     "origin": "123 Main Street",
     "destination": "456 Oak Avenue",
     "event": "ride_offered"
   }
   ```

   b. **notification** (to driver):
   ```json
   {
     "user_id": 102,
     "notification_type": "ride_offered",
     "title": "New Ride Available!",
     "message": "New ride from 123 Main Street to 456 Oak Avenue. Accept now!",
     "ride_id": 1,
     "event": "notification"
   }
   ```

6. **Acknowledges** message to RabbitMQ (removes from queue)

### Console Output

```
==========================================
 TAXI MATCHER WORKER
==========================================
RabbitMQ URL: amqp://guest:guest@localhost:5672/
Ride Service URL: http://localhost:8001/api/rides
Internal API URL: http://localhost:8001/api/internal
==========================================
 Connected to RabbitMQ
 Queues declared

==========================================
 LISTENING for messages on: ride.requested
   Press CTRL+C to stop
==========================================

============================================================
 RECEIVED: ride.requested
   Time: 10:05:23
   Data: {'ride_id': 1, 'passenger_id': 5, ...}
============================================================

 Searching driver for Ride #1
   Route: 123 Main Street → 456 Oak Avenue

 Driver found: ID=102
 Ride #1 updated with driver 102
 PUBLISHED: ride.offer
   Ride #1 offered to Driver #102
 PUBLISHED: notification to driver 102
 Message processed successfully
```

##  Notification Consumer Details

### How It Works

1. **Listens** to `notifications` queue
2. **Receives** notification message:
```json
{
  "user_id": 5,
  "notification_type": "ride_accepted",
  "title": "Driver Accepted Your Ride",
  "message": "A driver has accepted your ride! They will pick you up soon!",
  "ride_id": 1,
  "event": "notification"
}
```

3. **Processes** notification:
   - Extracts user ID, title, message
   - In production would:
     - Send email via SendGrid/AWS SES
     - Send SMS via Twilio
     - Send push via Firebase
     - Save to notification database

4. **Simulates** delivery:
   - Logs notification details
   - Adds 0.5s delay (simulating API call)
   - Confirms delivery

5. **Acknowledges** message

### Console Output

```
============================================================
NOTIFICATION CONSUMER WORKER
============================================================
RabbitMQ URL: amqp://guest:guest@localhost:5672/
============================================================
 Connected to RabbitMQ
 Queue declared

============================================================
 LISTENING for messages on: notifications
   Press CTRL+C to stop
============================================================

============================================================
RECEIVED: notifications
   Time: 10:05:25
============================================================

 Processing Notification:
   User: 5
   Type: ride_accepted
   Title: Driver Accepted Your Ride
   Message: A driver has accepted your ride! They will pick you up soon!
   Ride: 1

 Notification sent to user 5
 Notification processed successfully
```

## Message Flow Example

Complete flow from ride request to notification:

```
1. Passenger requests ride
   → Ride Service: POST /api/rides/
   → RabbitMQ: Publish to "ride.requested"

2. Matcher Worker receives
   → Finds driver (ID: 102)
   → Ride Service: POST /api/internal/rides/1/assign-driver/
   → RabbitMQ: Publish to "ride.offer"
   → RabbitMQ: Publish to "notifications" (for driver)

3. Notification Consumer receives
   → Processes notification for driver 102
   → Simulates sending (email/SMS/push)

4. Driver accepts via app
   → Ride Service: POST /api/rides/1/accept/
   → RabbitMQ: Publish to "notifications" (for passenger)

5. Notification Consumer receives
   → Processes notification for passenger
   → Simulates sending
```

## Testing

### Test Matcher Worker

1. **Start workers**
```bash
# Terminal 1
python matcher_worker.py

# Terminal 2
python notification_consumer.py
```

2. **Send test message** (or use Ride Service API)
```bash
python test_rabbitmq.py
```

3. **Watch console** for processing logs

### Test End-to-End

Use the full system test:
```bash
python ../test-full-system.py
```

This will:
1. Register user
2. Login
3. Request ride
4. Watch matcher assign driver
5. Check notifications

## Queue Configuration

### Queue: `ride.requested`
- **Producer**: Ride Service
- **Consumer**: Matcher Worker
- **Durable**: Yes
- **Message Format**:
```json
{
  "ride_id": 1,
  "passenger_id": 5,
  "origin": "string",
  "destination": "string",
  "event": "ride_requested"
}
```

### Queue: `ride.offer`
- **Producer**: Matcher Worker
- **Consumer**: (Future) Driver notification service
- **Durable**: Yes
- **Message Format**:
```json
{
  "ride_id": 1,
  "driver_id": 102,
  "passenger_id": 5,
  "origin": "string",
  "destination": "string",
  "event": "ride_offered"
}
```

### Queue: `notifications`
- **Producer**: Ride Service, Matcher Worker
- **Consumer**: Notification Consumer
- **Durable**: Yes
- **Message Format**:
```json
{
  "user_id": 5,
  "notification_type": "ride_accepted",
  "title": "string",
  "message": "string",
  "ride_id": 1,
  "event": "notification"
}
```

##  Security

### No Authentication Required
These workers use the **internal API** which bypasses JWT authentication:
- Endpoint: `/api/internal/rides/{id}/assign-driver/`
- Only accessible from internal network
- Should be protected by firewall in production

### Message Validation
Workers should validate all incoming messages:
```python
try:
    ride_data = json.loads(body)
    assert 'ride_id' in ride_data
    assert 'passenger_id' in ride_data
except (json.JSONDecodeError, AssertionError):
    logger.error("Invalid message format")
    channel.basic_nack(delivery_tag=method_frame.delivery_tag)
```

##  Production Considerations

### Current Implementation (Development)
- Simulated driver pool
- Random driver selection
- Console logging only
- No database persistence
- Single worker instances

### Production Recommendations

1. **Driver Matching Algorithm**
   - Query real driver database
   - Consider geolocation (distance to pickup)
   - Check driver availability status
   - Factor in driver ratings
   - Consider acceptance rate
   - Use ML for optimal matching

2. **Notification Delivery**
   - Integrate SendGrid/AWS SES for emails
   - Integrate Twilio for SMS
   - Integrate Firebase for push notifications
   - Store notifications in database
   - Implement retry logic

3. **Scalability**
   - Multiple worker instances
   - Load balancing across workers
   - Horizontal scaling with containers
   - Queue monitoring and alerts

4. **Error Handling**
   - Dead letter queues
   - Exponential backoff retry
   - Error logging to Sentry/DataDog
   - Health check endpoints

5. **Monitoring**
   - Queue depth monitoring
   - Processing time metrics
   - Error rate tracking
   - Worker health checks

### Example Production Setup

```python
# matcher_worker_prod.py
import redis
from celery import Celery

app = Celery('matcher', broker='redis://localhost:6379/0')

@app.task
def match_ride(ride_data):
    # Real driver database query
    drivers = Driver.objects.filter(
        status='available',
        location__distance_lte=(ride_data['pickup_location'], D(km=5))
    ).order_by('rating')
    
    if not drivers.exists():
        # Retry in 30 seconds
        match_ride.retry(countdown=30)
    
    driver = drivers.first()
    # ... assign logic
```

##  Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_URL` | RabbitMQ connection URL | `amqp://guest:guest@localhost:5672/` |
| `RIDE_SERVICE_URL` | Ride service base URL | `http://localhost:8001/api/rides` |
| `INTERNAL_API_URL` | Internal API base URL | `http://localhost:8001/api/internal` |

## Related Services

- [Ride Service](../ride-service/README.md)
- [Auth Service](../auth-service/README.md)
- [Root Documentation](../README.md)
