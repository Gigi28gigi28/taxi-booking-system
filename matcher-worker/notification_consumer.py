import json
import os
import pika
import time
from datetime import datetime

# Configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

print("=" * 60)
print(" NOTIFICATION CONSUMER WORKER")
print("=" * 60)
print(f"RabbitMQ URL: {RABBITMQ_URL}")
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

# 2. Notification Processing

def process_notification(notification_data):
    """
    Process notification based on type
    
    In production, this would:
    - Send email via SendGrid/AWS SES
    - Send SMS via Twilio
    - Send push notification via Firebase
    - Save to notification database
    
    For now: Just log to console
    """
    user_id = notification_data.get('user_id')
    notif_type = notification_data.get('notification_type')
    title = notification_data.get('title')
    message = notification_data.get('message')
    ride_id = notification_data.get('ride_id')
    
    print(f"\n Processing Notification:")
    print(f"   User: {user_id}")
    print(f"   Type: {notif_type}")
    print(f"   Title: {title}")
    print(f"   Message: {message}")
    print(f"   Ride: {ride_id}")
    
    # Simulate notification delivery
    time.sleep(0.5)
    
    # Here you would:
    # - Send email: send_email(user_id, title, message)
    # - Send SMS: send_sms(user_id, message)
    # - Send push: send_push(user_id, title, message)
    
    print(f" Notification sent to user {user_id}")

# 3. Message Callback

def on_notification_message(channel, method_frame, header_frame, body):
    """
    Callback when notification message is received
    """
    try:
        # Parse message
        notification_data = json.loads(body)
        
        print("\n" + "=" * 60)
        print(f" RECEIVED: notifications")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Process notification
        process_notification(notification_data)
        
        # Acknowledge message
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        
        print(" Notification processed successfully\n")
        
    except Exception as e:
        print(f"\n ERROR processing notification: {e}")
        import traceback
        traceback.print_exc()
        
        # Reject and requeue
        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)

# 4. Main Worker Loop

def start_worker():
    """
    Main worker function
    """
    print("\n Starting Notification Consumer...")
    
    # Connect
    connection = connect_rabbitmq()
    channel = connection.channel()
    
    # Declare queue (idempotent)
    channel.queue_declare(queue="notifications", durable=True)
    
    print(" Queue declared")
    
    # Set QoS - process one message at a time
    channel.basic_qos(prefetch_count=1)
    
    # Start consuming
    print("\n" + "=" * 60)
    print(" LISTENING for messages on: notifications")
    print("   Press CTRL+C to stop")
    print("=" * 60 + "\n")
    
    channel.basic_consume(
        queue="notifications",
        on_message_callback=on_notification_message
    )
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        channel.stop_consuming()
        connection.close()
        print(" Worker stopped")

# 5. Entry Point

if __name__ == "__main__":
    start_worker()