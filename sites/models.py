import os
import zipfile
import shutil
from django.db import models
from django.utils.text import slugify
from django.conf import settings

from offers.models import Offer


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class SiteArchive(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название архива/сайта")
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='site_offer', null=True)

    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='sites',
        null=True,
        verbose_name="Категория"
    )
    archive = models.FileField(upload_to='archives/', verbose_name="Архив")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    extracted_path = models.CharField(max_length=255, blank=True, default='extracted', verbose_name="Путь распаковки")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Слаг")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.extracted_path:
            extracted_folder = os.path.join(settings.MEDIA_ROOT, self.extracted_path)
            if os.path.exists(extracted_folder):
                shutil.rmtree(extracted_folder)  # Удаляем всю папку с распакованными файлами

            # Удаляем сам архив
        if self.archive:
            if os.path.exists(self.archive.path):
                os.remove(self.archive.path)

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'