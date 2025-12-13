from django.apps import AppConfig
import sys
import os


class ComptesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comptes'

    def ready(self):
        # Importer les signaux
        import comptes.signals
        
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