from celery import shared_task
from .models import OfferArchive

@shared_task
def check_for_repository_updates():
    archives = OfferArchive.objects.all()
    for archive in archives:
        if archive.check_for_updates():
            archive.update_repository()
            archive.save()
