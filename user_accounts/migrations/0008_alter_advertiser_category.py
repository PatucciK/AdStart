# Generated by Django 5.0.6 on 2024-11-25 12:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0007_category_advertiser_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertiser',
            name='category',
            field=models.ForeignKey(help_text='Категория рекламодателя', null=True, on_delete=django.db.models.deletion.CASCADE, to='user_accounts.category', verbose_name='Категория'),
        ),
    ]
