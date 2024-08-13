from django.db import models
from user_accounts.models import Advertiser
from django.core.exceptions import ValidationError


class PartnerCard(models.Model):
    advertiser = models.OneToOneField(Advertiser, on_delete=models.CASCADE, related_name='partner_card')
    logo = models.ImageField(upload_to='partner_logos/', blank=True, null=True, verbose_name='Логотип')
    name = models.CharField(max_length=255, verbose_name='Наименование')
    legal_name = models.CharField(max_length=255, verbose_name='Наименование Юр. лица')
    license = models.FileField(upload_to='licenses/', blank=True, null=True, verbose_name='Лицензия')
    website = models.URLField(verbose_name='Ссылка на официальный сайт')
    legal_address = models.CharField(max_length=255, verbose_name='Юридический адрес')
    actual_addresses = models.TextField(verbose_name='Фактический адрес')
    company_details = models.TextField(verbose_name='Реквизиты компании', blank=True, null=True, )
    contracts = models.FileField(upload_to='contracts/', blank=True, null=True,
                                 verbose_name='Договор, акты, доп. соглашения')
    main_phone = models.CharField(max_length=20, verbose_name='Телефон основной')
    deposit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Депозит', blank=True, null=True)
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен администратором')

    def clean(self):
        if self.is_approved and not self.deposit:
            raise ValidationError("Необходимо указать депозит для одобренной карточки партнера.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Карточка партнера'
        verbose_name_plural = 'Карточки партнеров'
