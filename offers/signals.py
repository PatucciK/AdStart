import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LeadWall
from .tasks import update_record

@receiver(post_save, sender=LeadWall)
def schedule_status_update(sender, instance, created, **kwargs):
    if created:
        # Планируем задачу на выполнение через 24 часа (86400 секунд)
        update_record.apply_async((instance.id,), countdown=86400)