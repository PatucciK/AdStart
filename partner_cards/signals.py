from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PartnerCard
from offers.models import Offer

@receiver(post_save, sender=PartnerCard)
def create_offer_for_partner_card(sender, instance, created, **kwargs):
    if instance.is_approved and not created:
        Offer.objects.get_or_create(
            partner_card=instance,
            defaults={
                'name': f"Оффер для {instance.name}",
                'legal_name': instance.legal_name,
                'website': instance.website,
                'legal_address': instance.legal_address,
                'actual_addresses': instance.actual_addresses,
                'working_hours': '',
                'service_description': 'Описание услуг по офферу',
                'geo': '',
                'lead_validity': '',
                'landing_page': '',
                'postback_documentation': '',
                'lead_price': 0.00
            }
        )
