from django.apps import AppConfig

class ComptesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comptes'

    def ready(self):
        from django.contrib.auth.models import Group
        from django.db.utils import OperationalError, ProgrammingError
        roles = [ 'passager', 'chauffeur']
        try:
            for r in roles:
                Group.objects.get_or_create(name=r)
        except (OperationalError, ProgrammingError):
            pass
