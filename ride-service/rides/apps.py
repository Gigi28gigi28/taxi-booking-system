from django.apps import AppConfig
import sys
import os


class RidesConfig(AppConfig):
    name = 'rides'

    def ready(self):
        # Enregistrement automatique dans Consul
        # Éviter double exécution (Django reload)
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
        
        # Lancer uniquement si on exécute runserver
        if 'runserver' in sys.argv:
            from .consul_utils import register_service
            
            # Petit délai pour laisser Django démarrer
            import time
            time.sleep(2)
            
            register_service()