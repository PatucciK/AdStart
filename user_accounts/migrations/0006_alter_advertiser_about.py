# Generated by Django 5.0.6 on 2024-10-25 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0005_advertiser_about'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertiser',
            name='about',
            field=models.TextField(blank=True, help_text='Описание услуги', max_length=500, verbose_name='Описание услуги'),
        ),
    ]
