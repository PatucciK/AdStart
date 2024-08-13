# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Advertiser, Webmaster

class AdvertiserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True, help_text='Обязательное поле.')
    username = serializers.CharField(source='user.username', required=True, help_text='Обязательное поле.')
    password = serializers.CharField(source='user.password', write_only=True, required=True, help_text='Обязательное поле.')
    telegram = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text='Необязательное поле.')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, help_text='Необязательное поле.')

    class Meta:
        model = Advertiser
        fields = ['email', 'username', 'password', 'telegram', 'phone']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        advertiser = Advertiser.objects.create(user=user, **validated_data)
        return advertiser

class WebmasterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True, help_text='Обязательное поле.')
    username = serializers.CharField(source='user.username', required=True, help_text='Обязательное поле.')
    password = serializers.CharField(source='user.password', write_only=True, required=True, help_text='Обязательное поле.')
    telegram = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text='Необязательное поле.')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, help_text='Необязательное поле.')
    experience = serializers.CharField(required=False, allow_blank=True, help_text='Необязательное поле.')
    stats_screenshot = serializers.ImageField(required=False, allow_null=True, help_text='Необязательное поле.')

    class Meta:
        model = Webmaster
        fields = ['email', 'username', 'password', 'telegram', 'phone', 'experience', 'stats_screenshot']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        webmaster = Webmaster.objects.create(user=user, **validated_data)
        return webmaster
