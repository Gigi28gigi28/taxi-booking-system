"""
Consul Service Discovery
Permet de découvrir dynamiquement les URLs des microservices
"""
import os
import requests
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

CONSUL_HOST = os.getenv('CONSUL_HOST', 'localhost')
CONSUL_PORT = os.getenv('CONSUL_PORT', '8500')

# Cache des services découverts (TTL: 60 secondes)
@lru_cache(maxsize=128)
def _get_consul_url():
    """Retourne l'URL de base de Consul"""
    return f"http://{CONSUL_HOST}:{CONSUL_PORT}"


def discover_service(service_name: str, fallback_url: Optional[str] = None) -> str:
    """
    Découvre l'URL d'un service via Consul
    
    Args:
        service_name: Nom du service dans Consul (ex: 'auth-service')
        fallback_url: URL de secours si Consul indisponible
    
    Returns:
        str: URL complète du service (ex: 'http://192.168.1.75:8000')
    
    Raises:
        Exception: Si le service n'est pas trouvé et pas de fallback
    
    Example:
        >>> discover_service('auth-service', 'http://localhost:8000')
        'http://127.0.0.1:8000'
    """
    try:
        consul_url = _get_consul_url()
        catalog_url = f"{consul_url}/v1/catalog/service/{service_name}"
        
        logger.debug(f" Discovering service: {service_name}")
        
        response = requests.get(catalog_url, timeout=3)
        
        if response.status_code == 200:
            services = response.json()
            
            if services:
                # Filtrer les services en bonne santé
                healthy_services = []
                
                for service in services:
                    # Vérifier le health check
                    service_id = service.get('ServiceID')
                    health_url = f"{consul_url}/v1/health/service/{service_name}?passing=true"
                    
                    try:
                        health_resp = requests.get(health_url, timeout=2)
                        if health_resp.status_code == 200:
                            health_data = health_resp.json()
                            
                            # Vérifier si ce service spécifique est en bonne santé
                            for entry in health_data:
                                if entry['Service']['ID'] == service_id:
                                    healthy_services.append(service)
                                    break
                    except:
                        # Si on ne peut pas vérifier, on considère le service comme disponible
                        healthy_services.append(service)
                
                # Utiliser le premier service en bonne santé
                if healthy_services:
                    service = healthy_services[0]
                    address = service['ServiceAddress'] or service['Address']
                    port = service['ServicePort']
                    
                    service_url = f"http://{address}:{port}"
                    logger.info(f"Service discovered: {service_name} → {service_url}")
                    return service_url
                elif services:
                    # Aucun service en bonne santé, utiliser le premier disponible
                    service = services[0]
                    address = service['ServiceAddress'] or service['Address']
                    port = service['ServicePort']
                    service_url = f"http://{address}:{port}"
                    logger.warning(f" Service {service_name} found but health unknown → {service_url}")
                    return service_url
        
        logger.warning(f" Service '{service_name}' not found in Consul")
        
    except requests.exceptions.Timeout:
        logger.error(f" Consul timeout when discovering '{service_name}'")
    except requests.exceptions.ConnectionError:
        logger.error(f" Cannot connect to Consul at {_get_consul_url()}")
    except Exception as e:
        logger.error(f" Consul discovery error for '{service_name}': {e}")
    
    # Fallback
    if fallback_url:
        logger.info(f" Using fallback URL for '{service_name}': {fallback_url}")
        return fallback_url
    
    raise Exception(f"Cannot discover service '{service_name}' and no fallback provided")


def discover_all_instances(service_name: str) -> list:
    """
    Récupère toutes les instances d'un service (pour load balancing manuel)
    
    Args:
        service_name: Nom du service
    
    Returns:
        list: Liste des URLs de toutes les instances
    
    Example:
        >>> discover_all_instances('auth-service')
        ['http://127.0.0.1:8000', 'http://127.0.0.1:8002']
    """
    try:
        consul_url = _get_consul_url()
        catalog_url = f"{consul_url}/v1/catalog/service/{service_name}"
        
        response = requests.get(catalog_url, timeout=3)
        
        if response.status_code == 200:
            services = response.json()
            
            instances = []
            for service in services:
                address = service['ServiceAddress'] or service['Address']
                port = service['ServicePort']
                instances.append(f"http://{address}:{port}")
            
            logger.info(f" Found {len(instances)} instances of '{service_name}'")
            return instances
        
    except Exception as e:
        logger.error(f" Error discovering all instances: {e}")
    
    return []


def is_consul_available() -> bool:
    """
    Vérifie si Consul est accessible
    
    Returns:
        bool: True si Consul répond, False sinon
    """
    try:
        consul_url = _get_consul_url()
        response = requests.get(f"{consul_url}/v1/status/leader", timeout=2)
        return response.status_code == 200
    except:
        return False


# Fonction de commodité pour l'auth service
def get_auth_service_url(fallback: str = "http://localhost:8000") -> str:
    """
    Raccourci pour découvrir l'auth-service
    
    Returns:
        str: URL de base de l'auth-service
    """
    return discover_service('auth-service', fallback_url=fallback)