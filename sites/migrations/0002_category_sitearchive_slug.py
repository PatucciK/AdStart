# Generated by Django 5.0.6 on 2024-11-26 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='sitearchive',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
