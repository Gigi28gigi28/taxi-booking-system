import json
import os
import pika
import time
import random

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

# -------------------------------
# 1. Connexion RabbitMQ
# -------------------------------

def connect():
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            print("✅ Connected to RabbitMQ")
            return connection
        except Exception as e:
            print("❌ RabbitMQ not ready, retrying...", e)
            time.sleep(3)

# -------------------------------
# 2. Trouver un chauffeur (fake)
# -------------------------------

def find_available_driver(ride_data):
    """
    Simulation simple :
    Dans un vrai système, tu ping un microservice Chauffeur
    ou une base de donnée spécialisée.
    """

    # Fake list de chauffeurs disponibles
    drivers = [101, 102, 103, 104, 105]

    # Tu peux remplacer avec un appel HTTP :
    # response = requests.get("http://driver-service/api/drivers/available")
    # drivers = response.json()

    print(f"🔍 Searching driver for ride {ride_data['ride_id']}...")

    time.sleep(2)  # simule un vrai matching

    selected = random.choice(drivers)

    print(f"🚗 Driver found: {selected}")
    return selected

# -------------------------------
# 3. Callback quand message reçu
# -------------------------------

def on_message(channel, method_frame, header_frame, body):
    ride_data = json.loads(body)
    print("\n📨 Received ride.requested:", ride_data)

    # Trouver chauffeur
    driver_id = find_available_driver(ride_data)

    # Construire event ride.offer
    offer_msg = {
        "ride_id": ride_data["ride_id"],
        "driver_id": driver_id,
        "origin": ride_data["origin"],
        "destination": ride_data["destination"],
        "passenger_id": ride_data["passenger_id"]
    }

    # Publier l’offre
    channel.basic_publish(
        exchange="",
        routing_key="ride.offer",
        body=json.dumps(offer_msg),
        properties=pika.BasicProperties(content_type='application/json')
    )

    print(f"📤 Published ride.offer: {offer_msg}")

    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

# -------------------------------
# 4. Main loop
# -------------------------------

def start_worker():
    connection = connect()
    channel = connection.channel()

    # Déclarer les queues
    channel.queue_declare(queue="ride.requested", durable=False)
    channel.queue_declare(queue="ride.offer", durable=False)

    print("👂 Listening on queue: ride.requested ...")

    channel.basic_consume(
        queue="ride.requested",
        on_message_callback=on_message
    )

    channel.start_consuming()


if __name__ == "__main__":
    start_worker()
