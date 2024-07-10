# Generated by Django 5.0.6 on 2024-07-10 16:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertiser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user_accounts.customadminuser'),
        ),
        migrations.AlterField(
            model_name='webmaster',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user_accounts.customadminuser'),
        ),
    ]
