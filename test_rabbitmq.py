import pika
import json

# Connect to RabbitMQ
try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()
    
    print("✅ Connected to RabbitMQ successfully!")
    
    # Declare queue (safe to call even if exists)
    channel.queue_declare(queue='ride.requested', durable=True)
    
    # Publish test message
    test_message = {
        "ride_id": 999,
        "passenger_id": 123,
        "origin": "Test Origin",
        "destination": "Test Destination"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='ride.requested',
        body=json.dumps(test_message),
        properties=pika.BasicProperties(
            content_type='application/json',
            delivery_mode=2  # make message persistent
        )
    )
    
    print(f"✅ Published test message: {test_message}")
    
    connection.close()
    
except Exception as e:
    print(f"❌ Error: {e}")