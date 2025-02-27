# Generated by Django 5.0.6 on 2024-12-02 18:28

import ckeditor.fields
import datetime
import django.db.models.deletion
import multiselectfield.db.fields
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('partner_cards', '0001_initial'),
        ('user_accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadWall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя пользователя')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_extra', models.TextField(blank=True, null=True, verbose_name='Дополнительно')),
                ('processing_status', models.CharField(choices=[('new', 'Новый лид'), ('expired', 'Просрочено'), ('no_response', 'Нет ответа'), ('callback', 'Перезвонить'), ('appointment', 'Запись на прием'), ('visit', 'Визит'), ('trash', 'Треш'), ('duplicate', 'Дубль'), ('rejected', 'Отклонено')], default='new', max_length=20, verbose_name='Статус обработки')),
                ('status', models.CharField(choices=[('paid', 'Оплачено'), ('on_hold', 'В работе'), ('cancelled', 'Отмена')], default='on_hold', max_length=20, verbose_name='Статус')),
                ('phone', models.CharField(max_length=15, verbose_name='Номер мобильного телефона')),
                ('sub_1', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 1')),
                ('sub_2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 2')),
                ('sub_3', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 3')),
                ('sub_4', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 4')),
                ('sub_5', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 5')),
                ('ip_adress', models.CharField(blank=True, max_length=100, null=True, verbose_name='IP адрес отправителя')),
                ('domain', models.CharField(blank=True, max_length=100, null=True, verbose_name='Доменное имя отправителя')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Лидвол',
                'verbose_name_plural': 'Лидволы',
            },
        ),
        migrations.CreateModel(
            name='ChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_object_id', models.PositiveIntegerField()),
                ('target_model', models.CharField(max_length=50)),
                ('field_name', models.CharField(max_length=50)),
                ('current_value', models.TextField()),
                ('requested_value', models.TextField()),
                ('approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Запрос на изменение лида',
                'verbose_name_plural': 'Запрос на изменение',
            },
        ),
        migrations.CreateModel(
            name='LeadComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('text', models.TextField(verbose_name='Текст комментария')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='offers.leadwall', verbose_name='Лид')),
            ],
            options={
                'verbose_name': 'Комментарий к лиду',
                'verbose_name_plural': 'Комментарии к лидам',
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='offer_logos/', verbose_name='Логотип')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование оффера')),
                ('inn', models.CharField(blank=True, max_length=12, null=True, verbose_name='ИНН')),
                ('contract_number', models.CharField(default='AUTO_GENERATE', max_length=50, verbose_name='Номер Договора')),
                ('contract_date', models.DateField(default=datetime.date.today, verbose_name='Дата договора')),
                ('working_hours', models.CharField(blank=True, max_length=255, null=True, verbose_name='Режим работы колл-центра')),
                ('service_description', ckeditor.fields.RichTextField(verbose_name='Описание услуг по офферу')),
                ('geo', models.CharField(blank=True, max_length=255, null=True, verbose_name='ГЕО')),
                ('offer_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена за оффер')),
                ('lead_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена за лид')),
                ('status', models.CharField(choices=[('registered', 'Регистрация'), ('active', 'Активен'), ('paused', 'Пауза'), ('stopped', 'СТОП')], default='registered', max_length=20, verbose_name='Актуальность')),
                ('public_status', models.CharField(choices=[('private', 'Закрытый'), ('public', 'Публичный')], default='private', max_length=20, verbose_name='Публичный статус')),
                ('validation_data_lead', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('new', 'Новый лид'), ('expired', 'Просрочено'), ('no_response', 'Нет ответа'), ('callback', 'Перезвонить'), ('appointment', 'Запись на прием'), ('visit', 'Визит'), ('trash', 'Треш'), ('duplicate', 'Дубль'), ('rejected', 'Отклонено')], max_length=75, verbose_name='Валидация данных (Рекл.)')),
                ('validation_data_web', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('new', 'Новый лид'), ('expired', 'Просрочено'), ('no_response', 'Нет ответа'), ('callback', 'Перезвонить'), ('appointment', 'Запись на прием'), ('visit', 'Визит'), ('trash', 'Треш'), ('duplicate', 'Дубль'), ('rejected', 'Отклонено')], max_length=75, verbose_name='Валидация данных (Веб.)')),
                ('partner_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='partner_cards.partnercard')),
            ],
            options={
                'verbose_name': 'Оффер',
                'verbose_name_plural': 'Офферы',
                'permissions': [('change_lead_price', 'Can change lead_price field')],
            },
        ),
        migrations.CreateModel(
            name='OfferArchive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repo_url', models.URLField(max_length=255, verbose_name='URL репозитория')),
                ('branch', models.CharField(default='main', max_length=255, verbose_name='Ветка репозитория')),
                ('cloned_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата клонирования')),
                ('last_update', models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')),
                ('local_repo_path', models.CharField(blank=True, max_length=255, null=True, verbose_name='Путь к локальному репозиторию')),
                ('last_commit_hash', models.CharField(blank=True, max_length=40, null=True, verbose_name='Хеш последнего коммита')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='archives', to='offers.offer')),
            ],
            options={
                'verbose_name': 'Архив оффера',
                'verbose_name_plural': 'Архивы офферов',
            },
        ),
        migrations.CreateModel(
            name='OfferWebmaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_token', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Уникальный токен для определения связи между оффером и вебмастером', unique=True, verbose_name='Уникальный токен')),
                ('phone', models.CharField(max_length=15, verbose_name='Номер мобильного телефона')),
                ('metrika_token', models.CharField(blank=True, max_length=255, null=True, verbose_name='Метрика токен')),
                ('validation_data_lead', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('new', 'Новый лид'), ('expired', 'Просрочено'), ('no_response', 'Нет ответа'), ('callback', 'Перезвонить'), ('appointment', 'Запись на прием'), ('visit', 'Визит'), ('trash', 'Треш'), ('duplicate', 'Дубль'), ('rejected', 'Отклонено')], max_length=75, verbose_name='Валидация данных')),
                ('rate_of_pay', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Ставка за лид')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webmaster_links', to='offers.offer')),
                ('webmaster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offer_links', to='user_accounts.webmaster')),
            ],
            options={
                'verbose_name': 'Связь Оффер-Вебмастер',
                'verbose_name_plural': 'Связи Оффер-Вебмастер',
                'unique_together': {('offer', 'webmaster')},
            },
        ),
        migrations.AddField(
            model_name='leadwall',
            name='offer_webmaster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='offers.offerwebmaster', verbose_name='Оффер-Вебмастер'),
        ),
        migrations.CreateModel(
            name='Click',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время трекинга клика')),
                ('click_data', models.TextField(blank=True, null=True, verbose_name='Данные о клиенте')),
                ('sub_1', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 1')),
                ('sub_2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 2')),
                ('sub_3', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 3')),
                ('sub_4', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 4')),
                ('sub_5', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 5')),
                ('ip_adress', models.CharField(blank=True, max_length=100, null=True, verbose_name='IP адрес отправителя')),
                ('domain', models.CharField(blank=True, max_length=100, null=True, verbose_name='Доменное имя отправителя')),
                ('offer_webmaster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='offers.offerwebmaster', verbose_name='Оффер-Вебмастер')),
            ],
            options={
                'verbose_name': 'Клик',
                'verbose_name_plural': 'Клики',
            },
        ),
    ]
