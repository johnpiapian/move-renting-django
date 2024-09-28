from django.apps import AppConfig
from django.core.management import call_command


class BricksmasherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BrickSmasher'

    def ready(self) -> None:
        call_command('migrate')