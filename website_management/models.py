from django.db import models
from offer_management.models import Offer
from user_accounts.models import Webmaster

class Site(models.Model):
    LANDING_TYPE_CHOICES = [
        ('land', 'Ленд'),
        ('quiz', 'Квиз'),
        ('clip', 'Клип')
    ]
    STATUS_CHOICES = [
        ('in_work', 'В работе'),
        ('on_pause', 'На паузе'),
        ('disabled', 'Выключена')
    ]
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        verbose_name='Оффер',
        help_text='Оффер, связанный с сайтом'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Название сайта'
    )
    archive = models.FileField(
        upload_to='archives/',
        verbose_name='Архив',
        help_text='Архив сайта'
    )
    landing_type = models.CharField(
        max_length=20,
        choices=LANDING_TYPE_CHOICES,
        verbose_name='Тип посадки',
        help_text='Тип посадки сайта'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Статус',
        help_text='Статус сайта'
    )
    path = models.CharField(
        max_length=255,
        verbose_name='Путь',
        help_text='Путь к сайту на сервере'
    )
    webmaster = models.ForeignKey(
        Webmaster,
        on_delete=models.CASCADE,
        verbose_name='Вебмастер',
        help_text='Вебмастер, связанный с сайтом'
    )

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'
