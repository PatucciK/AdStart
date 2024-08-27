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
    public_status = models.CharField(max_length=20, choices=PUBLIC_STATUS_CHOICES, default='private',
                                     verbose_name='Публичный статус')

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


class OfferWebmaster(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='webmaster_links')
    webmaster = models.ForeignKey(Webmaster, on_delete=models.CASCADE, related_name='offer_links')
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Уникальный токен',
                                    help_text='Уникальный токен для определения связи между оффером и вебмастером')
    phone = models.CharField(max_length=15, verbose_name='Номер мобильного телефона')
    metrika_token = models.CharField(max_length=255, verbose_name='Метрика токен', blank=True, null=True)

    def __str__(self):
        return f'{self.offer.name} - {self.webmaster.user.username}'

    class Meta:
        unique_together = ('offer', 'webmaster')
        verbose_name = 'Связь Оффер-Вебмастер'
        verbose_name_plural = 'Связи Оффер-Вебмастер'


class LeadWall(models.Model):
    LEAD_STATUS_CHOICES = [
        ('paid', 'Оплачено'),
        ('on_hold', 'В работе'),
        ('cancelled', 'Отмена'),
    ]

    PROCESSING_STATUS_CHOICES = [
        ('new', 'Новый лид'),
        ('expired', 'Просрочено'),
        ('no_response', 'Нет ответа'),
        ('callback', 'Перезвонить'),
        ('appointment', 'Запись на прием'),
        ('visit', 'Визит'),
        ('trash', 'Треш'),
        ('duplicate', 'Дубль'),
        ('rejected', 'Отклонено'),
    ]

    offer_webmaster = models.ForeignKey(OfferWebmaster, on_delete=models.CASCADE, related_name='leads',
                                        verbose_name='Оффер-Вебмастер')
    name = models.CharField(max_length=255, verbose_name='Имя пользователя', blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    description_extra = models.TextField(blank=True, null=True, verbose_name='Дополнительно')
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='new', verbose_name='Статус обработки')
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='on_hold', verbose_name='Статус')
    phone = models.CharField(max_length=15, verbose_name='Номер мобильного телефона')
    sub_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 1')
    sub_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 2')
    sub_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 3')
    sub_4 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 4')
    sub_5 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 5')
    ip_adress = models.CharField(max_length=100, verbose_name="IP адрес отправителя", blank=True, null=True)
    domain = models.CharField(max_length=100, verbose_name="Доменное имя отправителя", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(verbose_name='Дата обновления', blank=True, null=True)


    def __str__(self):
        return f'{self.name} - {self.status}'

    def can_change_to(self, new_status):
        """
        Проверяет, может ли текущий статус обработки быть изменен на новый.
        """
        unchangeable_statuses = {'paid', 'expired', 'trash', 'duplicate', 'rejected', 'visit'}
        if self.processing_status in unchangeable_statuses:
            return False
        if new_status in unchangeable_statuses and not self.offer_webmaster.offer.partner_card.advertiser.user.is_superuser:
            return False
        return True

    class Meta:
        verbose_name = 'Лидвол'
        verbose_name_plural = 'Лидволы'

class Click(models.Model):
    offer_webmaster = models.ForeignKey(OfferWebmaster, on_delete=models.CASCADE, related_name='clicks',
                                        verbose_name='Оффер-Вебмастер')
    created_at = models.DateTimeField(verbose_name="Время трекинга клика", auto_now_add=True)
    click_data = models.TextField(verbose_name="Данные о клиенте", blank=True, null=True)
    sub_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 1')
    sub_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 2')
    sub_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 3')
    sub_4 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 4')
    sub_5 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Sub 5')
    ip_adress = models.CharField(max_length=100, verbose_name="IP адрес отправителя", blank=True, null=True)
    domain = models.CharField(max_length=100, verbose_name="Доменное имя отправителя", blank=True, null=True)

    def __str__(self):
        return f"{self.offer_webmaster}"

    class Meta:
        verbose_name = 'Клик'
        verbose_name_plural = 'Клики'
