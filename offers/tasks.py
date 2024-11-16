from celery import shared_task
from .models import OfferArchive, LeadWall
from django.utils.timezone import now

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

        # Проверяем, прошло ли 24 часа с момента последнего обновления
        if now() - obj.update_at >= timedelta(minutes=1):
            obj.processing_status = 'expired'
            obj.status = 'paid'
            obj.save()
        else:
            return f'Запись {pk} не обновлена, так как прошло менее 24 часов с последнего изменения'

    except LeadWall.DoesNotExist:
        return f'Запись с ID {pk} не найдена'