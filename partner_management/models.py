from django.db import models
from user_accounts.models import CustomAdminUser, Advertiser


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Название категории'
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name='Приватная',
        help_text='Флаг приватности категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Partner(models.Model):
    admin_user = models.ForeignKey(
        CustomAdminUser,
        on_delete=models.CASCADE,
        verbose_name='Администратор',
        help_text='Администратор, связанный с партнером'
    )
    advertiser_user = models.ForeignKey(
        Advertiser,
        on_delete=models.CASCADE,
        verbose_name='Рекламодатель',
        help_text='Рекламодатель, связанный с партнером'
    )
    logo = models.ImageField(
        upload_to='logos/',
        verbose_name='Логотип',
        help_text='Логотип партнера'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Название партнера'
    )
    legal_name = models.CharField(
        max_length=255,
        verbose_name='Юридическое название',
        help_text='Юридическое название партнера'
    )
    license = models.FileField(
        upload_to='licenses/',
        verbose_name='Лицензия',
        help_text='Лицензия партнера'
    )
    official_website = models.URLField(
        verbose_name='Официальный сайт',
        help_text='Официальный сайт партнера'
    )
    legal_address = models.TextField(
        verbose_name='Юридический адрес',
        help_text='Юридический адрес партнера'
    )
    actual_address = models.TextField(
        verbose_name='Фактический адрес',
        help_text='Фактический адрес партнера'
    )
    company_details = models.TextField(
        verbose_name='Реквизиты компании',
        help_text='Реквизиты компании партнера'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        help_text='Основной телефон партнера'
    )
    deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Депозит',
        help_text='Депозит партнера'
    )

    class Meta:
        verbose_name = 'Карточка рекламодателя'
        verbose_name_plural = 'Карточки рекламодателей'
