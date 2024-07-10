from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Advertiser, Webmaster


class AdvertiserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, help_text="Пароль для учетной записи")

    class Meta:
        model = Advertiser
        fields = ['email', 'telegram', 'phone', 'password']
        extra_kwargs = {
            'email': {'help_text': 'Email для регистрации'},
            'telegram': {'help_text': 'Telegram ID или URL профиля'},
            'phone': {'help_text': 'Номер телефона в формате 10 цифр без +7'},
            'password': {'help_text': 'Пароль для учетной записи'},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class WebmasterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, help_text="Пароль для учетной записи")

    class Meta:
        model = Webmaster
        fields = ['email', 'telegram', 'phone', 'password', 'experience', 'stats_screenshot']
        extra_kwargs = {
            'email': {'help_text': 'Email для регистрации'},
            'telegram': {'help_text': 'Telegram ID или URL профиля'},
            'phone': {'help_text': 'Номер телефона в формате 10 цифр без +7'},
            'experience': {'help_text': 'Описание опыта работы в лидогенерации'},
            'stats_screenshot': {'help_text': 'Скриншот статистики по лидам'},
            'password': {'help_text': 'Пароль для учетной записи'},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
