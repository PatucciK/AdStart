from celery import shared_task
from django.utils.timezone import now
from celery.utils.log import get_task_logger
from django.apps import apps
from django.utils.timezone import localtime

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
        obj = LeadWall.objects.get(id=pk)
        if localtime(obj.created_at).strftime('%Y-%m-%d %H:%M:%S') == localtime(obj.update_at).strftime('%Y-%m-%d %H:%M:%S') and obj.processing_status == 'new':
            obj.processing_status = 'expired'
            obj.status = 'paid'
            obj.save()
            return f'Запись {pk} обновлена'
        else:
            return f'Запись {pk} не обновлена, так как прошло менее 24 часов с последнего изменения'

    except LeadWall.DoesNotExist:
        return f'Запись с ID {pk} не найдена'
    except Exception as ex:
        print(ex)