from django.apps import AppConfig

class PartnerCardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'partner_cards'

    def ready(self):
        import partner_cards.signals  # Импортируем сигналы
