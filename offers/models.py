from django.db import models
from partner_cards.models import PartnerCard
from user_accounts.models import Webmaster
from datetime import date, timedelta
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
    public_status = models.CharField(max_length=20, choices=PUBLIC_STATUS_CHOICES, default='private',
                                     verbose_name='Публичный статус')
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


class LeadWall(models.Model):
    LEAD_STATUS_CHOICES = [
        ('new', 'Новый лид'),
        ('expired', 'Просрочено'),
        ('paid', 'Оплачено'),
        ('no_response', 'Нет ответа'),
        ('on_hold', 'Холд'),
        ('callback', 'Перезвонить'),
        ('appointment', 'Запись на прием'),
        ('visit', 'Визит'),
        ('cancelled', 'Отмена'),
        ('trash', 'Треш'),
        ('duplicate', 'Дубль'),
    ]

    offer = models.OneToOneField(Offer, on_delete=models.CASCADE, to_field='unique_token', related_name='lead_wall',
                                 verbose_name='Оффер')
    name = models.CharField(max_length=255, verbose_name='Имя пользователя')
    phone = models.CharField(max_length=15, verbose_name='Номер мобильного телефона')
    description = models.TextField(blank=True, null=True, verbose_name='Дополнительное поле')
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new', verbose_name='Статус лида')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'{self.name} - {self.status}'

    def can_change_to(self, new_status):
        """
        Проверяет, может ли текущий статус быть изменен на новый.
        """
        unchangeable_statuses = {'paid', 'expired', 'trash', 'duplicate', 'rejected', 'visit'}
        if self.status in unchangeable_statuses:
            return False
        if new_status in unchangeable_statuses and not self.offer.partner_card.advertiser.user.is_superuser:
            return False
        return True

    class Meta:
        verbose_name = 'Лидвол'
        verbose_name_plural = 'Лидволы'
