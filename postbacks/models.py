from django.db import models

class Postback(models.Model):

    secret = models.CharField(verbose_name="Ключ API")
    name = models.CharField(verbose_name="Название сервиса партнера")

    class Meta:
        verbose_name="Постбэк"
        verbose_name_plural="Постбэки"        