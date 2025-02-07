from django.db import models
from partner_cards.models import PartnerCard
from django.utils.timezone import now
from user_accounts.models import Webmaster
from django.contrib.auth.models import User
from datetime import date
import uuid
import os
from git import Repo
from ckeditor.fields import RichTextField
from multiselectfield import MultiSelectField

from django.db.models.signals import post_save
from django.dispatch import receiver


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

    VALIDATION_CHOICES = [
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

    partner_card = models.ForeignKey(PartnerCard, on_delete=models.CASCADE, related_name='offers')
    logo = models.ImageField(upload_to='offer_logos/', blank=True, null=True, verbose_name='Логотип')
    name = models.CharField(max_length=255, verbose_name='Наименование оффера')
    inn = models.CharField(max_length=12, verbose_name='ИНН', blank=True, null=True)
    contract_number = models.CharField(max_length=50, verbose_name='Номер Договора', default='AUTO_GENERATE')
    contract_date = models.DateField(default=date.today, verbose_name='Дата договора')
    working_hours = models.CharField(max_length=255, blank=True, null=True, verbose_name='Режим работы колл-центра')
    service_description = RichTextField(verbose_name='Описание услуг по офферу')
    geo = models.CharField(max_length=255, blank=True, null=True, verbose_name='ГЕО')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за оффер', blank=True, null=True)
    lead_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за лид', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', verbose_name='Актуальность')
    public_status = models.CharField(max_length=20, choices=PUBLIC_STATUS_CHOICES, default='private',
                                     verbose_name='Публичный статус')

    # Новое поле "Валидация данных" с выбором нескольких значений
    validation_data_lead = MultiSelectField(choices=VALIDATION_CHOICES, verbose_name='Валидация данных (Рекл.)', blank=True)
    validation_data_web = MultiSelectField(choices=VALIDATION_CHOICES, verbose_name='Валидация данных (Веб.)', blank=True)


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
        permissions = [
            ("change_lead_price", "Can change lead_price field"),
        ]

class OfferArchive(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='archives')
    repo_url = models.URLField(max_length=255, verbose_name='URL репозитория')
    branch = models.CharField(max_length=255, verbose_name='Ветка репозитория', default='main')
    cloned_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата клонирования', null=True)
    last_update = models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')
    local_repo_path = models.CharField(max_length=255, blank=True, null=True, verbose_name='Путь к локальному репозиторию')
    last_commit_hash = models.CharField(max_length=40, blank=True, null=True, verbose_name='Хеш последнего коммита')

    def __str__(self):
        return f"Archive for {self.offer.name}"

    def save(self, *args, **kwargs):
        # Устанавливаем путь к локальному репозиторию
        if not self.local_repo_path:
            self.local_repo_path = os.path.join(settings.BASE_DIR, 'archives', f'{self.offer.id}')

        # Если репозиторий уже существует, проверяем изменения
        if os.path.exists(self.local_repo_path):
            if self.check_for_updates():
                self.update_repository()
        else:
            self.clone_repository()

        super().save(*args, **kwargs)

    def clone_repository(self):
        """Клонируем репозиторий с GitHub."""
        try:
            repo = Repo.clone_from(self.repo_url, self.local_repo_path, branch=self.branch)
            self.last_commit_hash = repo.head.commit.hexsha  # Сохраняем хеш последнего коммита
            print(f'Repository {self.repo_url} cloned successfully.')
        except Exception as e:
            print(f'Error while cloning repository: {e}')

    def check_for_updates(self):
        """Проверяем, есть ли изменения в удаленном репозитории."""
        try:
            repo = Repo(self.local_repo_path)
            origin = repo.remotes.origin
            origin.fetch()  # Получаем информацию об изменениях без обновления
            remote_commit_hash = origin.refs[self.branch].commit.hexsha  # Хеш последнего коммита на удаленной ветке

            if remote_commit_hash != self.last_commit_hash:
                print(f'New changes detected in {self.repo_url}.')
                return True
            else:
                print(f'No changes in {self.repo_url}.')
                return False
        except Exception as e:
            print(f'Error while checking for updates: {e}')
            return False

    def update_repository(self):
        """Обновляем репозиторий с GitHub только если есть изменения."""
        try:
            repo = Repo(self.local_repo_path)
            repo.git.checkout(self.branch)
            repo.remotes.origin.pull()
            self.last_commit_hash = repo.head.commit.hexsha  # Обновляем хеш последнего коммита
            print(f'Repository {self.repo_url} updated successfully.')
        except Exception as e:
            print(f'Error while updating repository: {e}')

    class Meta:
        verbose_name = 'Архив оффера'
        verbose_name_plural = 'Архивы офферов'


class OfferWebmaster(models.Model):

    VALIDATION_CHOICES = [
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

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='webmaster_links')
    webmaster = models.ForeignKey(Webmaster, on_delete=models.CASCADE, related_name='offer_links')
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Уникальный токен',
                                    help_text='Уникальный токен для определения связи между оффером и вебмастером')
    phone = models.CharField(max_length=15, verbose_name='Номер мобильного телефона')
    metrika_token = models.CharField(max_length=255, verbose_name='Метрика токен', blank=True, null=True)

    validation_data_lead = MultiSelectField(choices=VALIDATION_CHOICES, verbose_name='Валидация данных', blank=True)
    rate_of_pay = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ставка за лид', blank=True, null=True)

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
                                        verbose_name='Оффер-Вебмастер', null=True)
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
    update_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)


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


class LeadComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Пользователь')
    lead = models.ForeignKey(LeadWall, on_delete=models.CASCADE, related_name='comments', verbose_name='Лид')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    text = models.TextField(verbose_name='Текст комментария')

    def __str__(self):
        return f"Комментарий от {self.user.username} для лида {self.lead.id}"

    class Meta:
        verbose_name = 'Комментарий к лиду'
        verbose_name_plural = 'Комментарии к лидам'


class ChangeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target_model = models.CharField(max_length=50)  # Имя модели, например, "Offer"
    field_name = models.CharField(max_length=50)  # Имя поля, которое нужно изменить
    current_value = models.TextField()  # Текущее значение поля
    requested_value = models.TextField()  # Новое значение, которое пользователь хочет установить
    approved = models.BooleanField(default=False)  # Поле для одобрения запроса администратором
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Change request by {self.user} for {self.field_name} in {self.target_model}"

    class Meta:
        verbose_name = 'Запрос на изменение лида'
        verbose_name_plural = 'Запрос на изменение'

class ExternalLeadwallMapping(models.Model):
    external_id = models.CharField(null=False, blank=False)
    local_id=models.ForeignKey(LeadWall,on_delete=models.CASCADE, null=False, blank=False)