import json
import os
import pika
import time
import random
import requests
from datetime import datetime

# Configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
RIDE_SERVICE_URL = os.getenv("RIDE_SERVICE_URL", "http://localhost:8001/api/rides")
# Internal API endpoint (no auth required)
INTERNAL_API_URL = os.getenv("INTERNAL_API_URL", "http://localhost:8001/api/internal")

print("=" * 60)
print("🚗 TAXI MATCHER WORKER")
print("=" * 60)
print(f"RabbitMQ URL: {RABBITMQ_URL}")
print(f"Ride Service URL: {RIDE_SERVICE_URL}")
print(f"Internal API URL: {INTERNAL_API_URL}")
print("=" * 60)

# 1. Connection Management

def connect_rabbitmq():
    """Connect to RabbitMQ with retry logic"""
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            print(" Connected to RabbitMQ")
            return connection
        except Exception as e:
            print(f" RabbitMQ not ready, retrying in 3s... ({e})")
            time.sleep(3)

# 2. Driver Matching Logic

def find_available_driver(ride_data):
    """
    Find available driver for the ride
    
    In production, this would:
    - Query driver database for available drivers
    - Check driver location vs pickup location
    - Consider driver ratings, acceptance rate
    - Use ML for optimal matching
    
    For now: Simple simulation with fake drivers
    """
    ride_id = ride_data.get('ride_id')
    origin = ride_data.get('origin')
    destination = ride_data.get('destination')
    
    print(f"\nSearching driver for Ride #{ride_id}")
    print(f"   Route: {origin} → {destination}")
    
    # Simulate matching delay (real-world: API calls, database queries)
    time.sleep(2)
    
    # Fake driver pool
    # In production: requests.get(f"{DRIVER_SERVICE_URL}/available")
    available_drivers = [101, 102, 103, 104, 105]
    
    # Simple selection (could be smart algorithm)
    selected_driver = random.choice(available_drivers)
    
    print(f" Driver found: ID={selected_driver}")
    
    return selected_driver

# 3. Update Ride in Database

def update_ride_with_driver(ride_id, driver_id):
    """
    Update ride status and assign driver
    Uses INTERNAL API (no authentication required)
    """
    try:
        # Use internal API endpoint (bypasses JWT)
        url = f"{INTERNAL_API_URL}/rides/{ride_id}/assign-driver/"
        payload = {"driver_id": driver_id}
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f" Ride #{ride_id} updated with driver {driver_id}")
            return True
        else:
            print(f" Failed to update ride: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f" Error updating ride: {e}")
        return False

# 4. Message Processing Callback

def on_ride_requested(channel, method_frame, header_frame, body):
    """
    Callback when ride.requested message is received
    
    Flow:
    1. Parse ride data
    2. Find available driver
    3. Update ride with driver
    4. Publish ride.offer event
    5. Acknowledge message
    """
    try:
        # Parse message
        ride_data = json.loads(body)
        
        print("\n" + "=" * 60)
        print(f" RECEIVED: ride.requested")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Data: {ride_data}")
        print("=" * 60)
        
        # Extract data
        ride_id = ride_data.get('ride_id')
        passenger_id = ride_data.get('passenger_id')
        origin = ride_data.get('origin')
        destination = ride_data.get('destination')
        
        # Find driver
        driver_id = find_available_driver(ride_data)
        
        # Update ride in database
        update_success = update_ride_with_driver(ride_id, driver_id)
        
        if not update_success:
            print("Failed to update ride, will retry")
            # Don't acknowledge - message will be redelivered
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
            return
        
        # Publish ride.offer event
        offer_message = {
            "ride_id": ride_id,
            "driver_id": driver_id,
            "passenger_id": passenger_id,
            "origin": origin,
            "destination": destination,
            "event": "ride_offered"
        }
        
        channel.basic_publish(
            exchange="",
            routing_key="ride.offer",
            body=json.dumps(offer_message),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2
            )
        )
        
        print(f" PUBLISHED: ride.offer")
        print(f"   Ride #{ride_id} offered to Driver #{driver_id}")
        
        #  NEW: Publish notification to driver
        notification_message = {
            "user_id": driver_id,
            "notification_type": "ride_offered",
            "title": "New Ride Available!",
            "message": f"New ride from {origin} to {destination}. Accept now!",
            "ride_id": ride_id,
            "event": "notification"
        }
        
        channel.basic_publish(
            exchange="",
            routing_key="notifications",
            body=json.dumps(notification_message),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2
            )
        )
        
        print(f" PUBLISHED: notification to driver {driver_id}")
        
        # Acknowledge message (remove from queue)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        
        print(" Message processed successfully\n")
        
    except Exception as e:
        print(f"\n ERROR processing message: {e}")
        import traceback
        traceback.print_exc()
        
        # Reject and requeue message
        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)

# 5. Main Worker Loop

def start_worker():
    """
    Main worker function
    - Connects to RabbitMQ
    - Declares queues
    - Starts consuming messages
    """
    print("\nStarting Matcher Worker...")
    
    # Connect
    connection = connect_rabbitmq()
    channel = connection.channel()
    
    # Declare queues (idempotent)
    channel.queue_declare(queue="ride.requested", durable=True)
    channel.queue_declare(queue="ride.offer", durable=True)
    
    print(" Queues declared")
    
    # Set QoS - process one message at a time
    channel.basic_qos(prefetch_count=1)
    
    # Start consuming
    print("\n" + "=" * 60)
    print(" LISTENING for messages on: ride.requested")
    print("   Press CTRL+C to stop")
    print("=" * 60 + "\n")
    
    channel.basic_consume(
        queue="ride.requested",
        on_message_callback=on_ride_requested
    )
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\n Shutting down gracefully...")
        channel.stop_consuming()
        connection.close()
        print("Worker stopped")

# 6. Entry Point

if __name__ == "__main__":
    start_worker()