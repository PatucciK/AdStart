from django.apps import AppConfig

class OffersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offers'

    def ready(self):
        import offers.signals  # Импортируйте сигналы