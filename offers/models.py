from django.db import models
from partner_cards.models import PartnerCard
from user_accounts.models import Webmaster
from datetime import date
import uuid

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

    partner_card = models.ForeignKey(PartnerCard, on_delete=models.CASCADE, related_name='offers')
    logo = models.ImageField(upload_to='offer_logos/', blank=True, null=True, verbose_name='Логотип')
    name = models.CharField(max_length=255, verbose_name='Наименование оффера')
    inn = models.CharField(max_length=12, verbose_name='ИНН', blank=True, null=True)
    contract_number = models.CharField(max_length=50, verbose_name='Номер Договора', default='AUTO_GENERATE')
    contract_date = models.DateField(default=date.today, verbose_name='Дата договора')
    working_hours = models.CharField(max_length=255, blank=True, null=True, verbose_name='Режим работы колл-центра')
    service_description = models.TextField(verbose_name='Описание услуг по офферу')
    geo = models.CharField(max_length=255, blank=True, null=True, verbose_name='ГЕО')
    lead_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за лид', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', verbose_name='Актуальность')
    public_status = models.CharField(max_length=20, choices=PUBLIC_STATUS_CHOICES, default='private', verbose_name='Публичный статус')
    webmaster = models.ForeignKey(Webmaster, on_delete=models.SET_NULL, blank=True, null=True, related_name='offers')
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Уникальный токен',
                                    help_text='Уникальный токен для определения связи между оффером и вебмастером')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.contract_number == 'AUTO_GENERATE':
            self.contract_number = self.generate_contract_number()
        super().save(*args, **kwargs)

    def generate_contract_number(self):
        return "CN-" + str(Offer.objects.count() + 1)

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural = 'Офферы'
