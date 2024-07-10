from django.db import models
from partner_management.models import Partner

class Offer(models.Model):
    STATUS_CHOICES = [
        ('registration', 'Регистрация'),
        ('active', 'Активен'),
        ('pause', 'Пауза'),
        ('stop', 'СТОП')
    ]
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name='Партнер',
        help_text='Партнер, связанный с оффером'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Статус',
        help_text='Статус оффера'
    )
    logo = models.ImageField(
        upload_to='logos/',
        verbose_name='Логотип',
        help_text='Логотип оффера'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Название оффера'
    )
    legal_name = models.CharField(
        max_length=255,
        verbose_name='Юридическое название',
        help_text='Юридическое название оффера'
    )
    inn = models.CharField(
        max_length=20,
        verbose_name='ИНН',
        help_text='ИНН оффера'
    )
    contract_number = models.CharField(
        max_length=50,
        verbose_name='Номер договора',
        help_text='Номер договора оффера'
    )
    contract_date = models.DateField(
        verbose_name='Дата договора',
        help_text='Дата договора оффера'
    )
    license = models.FileField(
        upload_to='licenses/',
        verbose_name='Лицензия',
        help_text='Лицензия оффера'
    )
    official_website = models.URLField(
        verbose_name='Официальный сайт',
        help_text='Официальный сайт оффера'
    )
    legal_address = models.TextField(
        verbose_name='Юридический адрес',
        help_text='Юридический адрес оффера'
    )
    actual_address = models.TextField(
        verbose_name='Фактический адрес',
        help_text='Фактический адрес оффера'
    )
    working_hours = models.CharField(
        max_length=255,
        verbose_name='Режим работы',
        help_text='Режим работы оффера'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание оффера'
    )
    geo = models.CharField(
        max_length=255,
        verbose_name='ГЕО',
        help_text='ГЕО оффера'
    )
    lead_validity = models.CharField(
        max_length=255,
        verbose_name='Валидность лида',
        help_text='Валидность лида оффера'
    )
    landing_page_url = models.URLField(
        verbose_name='Ссылка на посадочную страницу',
        help_text='Ссылка на посадочную страницу оффера'
    )
    post_request_docs = models.TextField(
        verbose_name='Документация по постзапросам',
        help_text='Документация по постзапросам оффера'
    )
    lead_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за лид',
        help_text='Цена за лид оффера'
    )

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural = 'Офферы'
