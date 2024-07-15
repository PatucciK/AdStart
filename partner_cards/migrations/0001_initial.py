# Generated by Django 5.0.6 on 2024-07-15 12:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_accounts', '0003_alter_advertiser_user_alter_webmaster_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='partner_logos/', verbose_name='Логотип')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('legal_name', models.CharField(max_length=255, verbose_name='Наименование Юр. лица')),
                ('license', models.FileField(blank=True, null=True, upload_to='licenses/', verbose_name='Лицензия')),
                ('website', models.URLField(blank=True, null=True, verbose_name='Ссылка на официальный сайт')),
                ('legal_address', models.CharField(max_length=255, verbose_name='Юридический адрес')),
                ('actual_addresses', models.TextField(blank=True, null=True, verbose_name='Фактический адрес')),
                ('company_details', models.TextField(verbose_name='Реквизиты компании')),
                ('contracts', models.FileField(blank=True, null=True, upload_to='contracts/', verbose_name='Договор, акты, доп. соглашения')),
                ('main_phone', models.CharField(max_length=20, verbose_name='Телефон основной')),
                ('deposit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Депозит')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Одобрен администратором')),
                ('advertiser', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='partner_card', to='user_accounts.advertiser')),
            ],
            options={
                'verbose_name': 'Карточка партнера',
                'verbose_name_plural': 'Карточки партнеров',
            },
        ),
    ]
