import os
import zipfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import SiteArchive

@receiver(post_save, sender=SiteArchive)
def extract_archive(sender, instance, created, **kwargs):
    """ Распаковка архива после сохранения """
    if created and instance.archive:
        archive_path = instance.archive.path
        target_dir = os.path.join(
            settings.MEDIA_ROOT, 'extracted', f"{instance.category.slug}", f"{instance.slug}"
        )
        os.makedirs(target_dir, exist_ok=True)

        # Распаковка архива
        if os.path.exists(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)

        # Обновление пути распакованных файлов
        instance.extracted_path = target_dir.replace(str(settings.MEDIA_ROOT), '').lstrip('/\\')
        instance.save(update_fields=['extracted_path'])