import os
import json
import pika
import logging

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def get_rabbitmq_connection():
    """
    Create RabbitMQ connection with retry logic
    """
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        return None

def publish_message(routing_key: str, message: dict, exchange: str = ""):
    """
    Publish message to RabbitMQ queue
    
    Args:
        routing_key: Queue name (e.g., 'ride.requested')
        message: Dictionary to send as JSON
        exchange: Exchange name (empty string for default)
    
    Returns:
        bool: True if successful, False otherwise
    """
    connection = None
    try:
        connection = get_rabbitmq_connection()
        
        if not connection:
            logger.error("Cannot publish: No RabbitMQ connection")
            return False
        
        channel = connection.channel()
        
        # Declare queue (idempotent - safe to call multiple times)
        channel.queue_declare(queue=routing_key, durable=True)
        
        # Publish message
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2  # Make message persistent
            )
        )
        
        logger.info(f"Published to '{routing_key}': {message}")
        return True
        
    except Exception as e:
        logger.error(f" Failed to publish to '{routing_key}': {e}")
        return False
        
    finally:
        if connection and not connection.is_closed:
            connection.close()

def publish_ride_requested(ride_id: int, passenger_id: int, origin: str, destination: str):
    """
    Publish ride request to matcher worker
    Also send notification to passenger
    """
    # Publish to matcher
    message = {
        "ride_id": ride_id,
        "passenger_id": passenger_id,
        "origin": origin,
        "destination": destination,
        "event": "ride_requested"
    }
    publish_message("ride.requested", message)
    
    # Send notification to passenger
    publish_notification(
        user_id=passenger_id,
        notification_type="ride_requested",
        title="Ride Request Received",
        message=f"Your ride from {origin} to {destination} has been requested. Searching for a driver...",
        ride_id=ride_id
    )
    return True

def publish_ride_accepted(ride_id: int, driver_id: int, passenger_id: int):
    """
    Publish ride acceptance notification
    """
    # Publish event
    message = {
        "ride_id": ride_id,
        "driver_id": driver_id,
        "passenger_id": passenger_id,
        "event": "ride_accepted"
    }
    publish_message("ride.accepted", message)
    
    # Notify passenger
    publish_notification(
        user_id=passenger_id,
        notification_type="ride_accepted",
        title="Driver Accepted Your Ride!",
        message=f"A driver has accepted your ride #{ride_id}. They will pick you up soon!",
        ride_id=ride_id
    )
    return True

def publish_ride_completed(ride_id: int, driver_id: int, passenger_id: int, price: float):
    """
    Publish ride completion notification
    """
    message = {
        "ride_id": ride_id,
        "driver_id": driver_id,
        "passenger_id": passenger_id,
        "price": str(price),
        "event": "ride_completed"
    }
    return publish_message("ride.completed", message)

def publish_ride_cancelled(ride_id: int, cancelled_by: int, reason: str = ""):
    """
    Publish ride cancellation notification
    """
    message = {
        "ride_id": ride_id,
        "cancelled_by": cancelled_by,
        "reason": reason,
        "event": "ride_cancelled"
    }
    return publish_message("ride.cancelled", message)

def publish_notification(user_id: int, notification_type: str, title: str, message: str, ride_id: int = None):
    """
    Publish notification to notifications queue
    """
    payload = {
        "user_id": user_id,
        "notification_type": notification_type,
        "title": title,
        "message": message,
        "ride_id": ride_id,
        "event": "notification"
    }
    return publish_message("notifications", payload)