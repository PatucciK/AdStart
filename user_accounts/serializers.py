from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Advertiser, Webmaster

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class AdvertiserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Advertiser
        fields = ['user', 'telegram', 'phone']

    def create(self, validated_data):
        # Извлекаем данные для пользователя
        user_data = validated_data.pop('user')
        # Создаем пользователя
        user = User.objects.create_user(**user_data)
        # Создаем рекламодателя, привязанного к пользователю
        advertiser = Advertiser.objects.create(user=user, **validated_data)
        return advertiser

class WebmasterSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Webmaster
        fields = ['user', 'telegram', 'phone', 'experience', 'stats_screenshot']

    def create(self, validated_data):
        # Извлекаем данные для пользователя
        user_data = validated_data.pop('user')
        # Создаем пользователя
        user = User.objects.create_user(**user_data)
        # Создаем вебмастера, привязанного к пользователю
        webmaster = Webmaster.objects.create(user=user, **validated_data)
        return webmaster
