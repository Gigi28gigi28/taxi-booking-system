"""
Consul Service Registry pour Ride-Service
"""
import os
import requests
import atexit
import logging

logger = logging.getLogger(__name__)

CONSUL_HOST = os.getenv('CONSUL_HOST', 'localhost')
CONSUL_PORT = os.getenv('CONSUL_PORT', '8500')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'ride-service')
SERVICE_PORT = int(os.getenv('SERVICE_PORT', '8001'))
SERVICE_HOST = os.getenv('SERVICE_HOST', '127.0.0.1')


def register_service():
    """
    Enregistre le service Ride dans Consul avec health check
    """
    service_id = f"{SERVICE_NAME}-{SERVICE_PORT}"
    
    service_data = {
        "ID": service_id,
        "Name": SERVICE_NAME,
        "Address": SERVICE_HOST,
        "Port": SERVICE_PORT,
        "Tags": [
            "traefik.enable=true",
            f"traefik.http.routers.{SERVICE_NAME}.rule=PathPrefix(`/api/rides`) || PathPrefix(`/api/notifications`) || PathPrefix(`/api/internal`)",
            f"traefik.http.services.{SERVICE_NAME}.loadbalancer.server.port={SERVICE_PORT}",
            "traefik.http.routers.ride-service.priority=90"
        ],
        "Check": {
            "HTTP": f"http://{SERVICE_HOST}:{SERVICE_PORT}/admin/login/",
            "Interval": "10s",
            "Timeout": "3s"
        }
    }
    
    try:
        url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"
        response = requests.put(url, json=service_data, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"Ride-Service enregistré dans Consul: {service_id}")
            logger.info(f"   → {SERVICE_HOST}:{SERVICE_PORT}")
            
            # Enregistrer le désenregistrement à la fermeture
            atexit.register(deregister_service, service_id)
        else:
            logger.error(f" Échec d'enregistrement Consul: {response.status_code}")
            
    except Exception as e:
        logger.error(f" Erreur connexion Consul: {e}")


def deregister_service(service_id):
    """
    Désenregistre le service de Consul à l'arrêt
    """
    try:
        url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/deregister/{service_id}"
        requests.put(url, timeout=3)
        logger.info(f" Ride-Service désenregistré de Consul: {service_id}")
    except Exception as e:
        logger.warning(f" Erreur désenregistrement: {e}")