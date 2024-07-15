from django.db import models
from partner_cards.models import PartnerCard
from datetime import date

class Offer(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Регистрация'),
        ('active', 'Активен'),
        ('paused', 'Пауза'),
        ('stopped', 'СТОП'),
    ]

    PUBLIC_STATUS_CHOICES = [
        ('private', 'Закрытый'),
        ('public', 'Публичный'),
    ]

    partner_card = models.OneToOneField(PartnerCard, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Наименование')
    legal_name = models.CharField(max_length=255, verbose_name='Наименование Юр. лица')
    website = models.URLField(blank=True, null=True, verbose_name='Ссылка на официальный сайт')
    legal_address = models.CharField(max_length=255, verbose_name='Юридический адрес')
    actual_addresses = models.TextField(blank=True, null=True, verbose_name='Фактический адрес')
    working_hours = models.CharField(max_length=255, blank=True, null=True, verbose_name='Режим работы')
    service_description = models.TextField(verbose_name='Описание услуг по офферу')
    geo = models.CharField(max_length=255, blank=True, null=True, verbose_name='ГЕО')
    lead_validity = models.CharField(max_length=255, blank=True, null=True, verbose_name='Валидность лида')
    landing_page = models.URLField(blank=True, null=True, verbose_name='Ссылка на посадку')
    postback_documentation = models.TextField(blank=True, null=True, verbose_name='Документация по отправке постзапросов')
    lead_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за лид', blank=True, null=True)
    contract_date = models.DateField(default=date.today, verbose_name='Дата договора')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', verbose_name='Актуальность')
    public_status = models.CharField(max_length=20, choices=PUBLIC_STATUS_CHOICES, default='private', verbose_name='Публичный статус')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural = 'Офферы'
