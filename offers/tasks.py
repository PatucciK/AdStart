from celery import shared_task
from django.utils.timezone import now
from celery.utils.log import get_task_logger
from django.apps import apps

from .models import LeadWall, OfferArchive

@shared_task
def check_for_repository_updates():
    archives = OfferArchive.objects.all()
    for archive in archives:
        if archive.check_for_updates():
            archive.update_repository()
            archive.save()

@shared_task
def update_record(pk):
    try:
        obj = LeadWall.objects.get(pk=pk)
        if obj.created_at == obj.updated_at:

            obj.processing_status = 'expired'
            obj.status = 'paid'
            obj.save()
        else:
            return f'Запись {pk} не обновлена, так как прошло менее 24 часов с последнего изменения'

    except LeadWall.DoesNotExist:
        return f'Запись с ID {pk} не найдена'