# Generated by Django 5.0.6 on 2024-08-21 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0015_leadwall_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadwall',
            name='description_extra',
            field=models.TextField(blank=True, null=True, verbose_name='Дополнительно'),
        ),
        migrations.AddField(
            model_name='leadwall',
            name='sub_1',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 1'),
        ),
        migrations.AddField(
            model_name='leadwall',
            name='sub_2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 2'),
        ),
        migrations.AddField(
            model_name='leadwall',
            name='sub_3',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 3'),
        ),
        migrations.AddField(
            model_name='leadwall',
            name='sub_4',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 4'),
        ),
        migrations.AddField(
            model_name='leadwall',
            name='sub_5',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub 5'),
        ),
        migrations.AddField(
            model_name='leadwall',
            name='update_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления'),
        ),
        migrations.AddField(
            model_name='offerwebmaster',
            name='metrika_token',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Метрика токен'),
        ),
        migrations.AlterField(
            model_name='leadwall',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='leadwall',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя пользователя'),
        ),
    ]
