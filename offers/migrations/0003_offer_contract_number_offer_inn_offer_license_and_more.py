# Generated by Django 5.0.6 on 2024-07-24 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0002_remove_offer_assigned_webmasters_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='contract_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Номер Договора'),
        ),
        migrations.AddField(
            model_name='offer',
            name='inn',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name='ИНН'),
        ),
        migrations.AddField(
            model_name='offer',
            name='license',
            field=models.FileField(blank=True, null=True, upload_to='offer_licenses/', verbose_name='Лицензия'),
        ),
        migrations.AddField(
            model_name='offer',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='offer_logos/', verbose_name='Логотип'),
        ),
    ]
