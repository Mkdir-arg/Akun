from django.apps import AppConfig


class LegacyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.legacy'
    verbose_name = 'Fuentes Legacy'

