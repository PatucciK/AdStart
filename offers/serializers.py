from rest_framework import serializers
from .models import Offer, LeadWall


class LeadWallSerializer(serializers.Serializer):
    unique_token = serializers.UUIDField(required=True, help_text="Уникальный токен оффера для идентификации")
    name = serializers.CharField(max_length=255, required=True, help_text="Имя пользователя, отправляющего лид")
    phone = serializers.CharField(max_length=15, required=True,
                                  help_text="Номер телефона пользователя в формате +7XXXXXXXXXX или 8XXXXXXXXXX")

    def validate_phone(self, value):
        if not (value.startswith('+7') or value.startswith('8')):
            raise serializers.ValidationError("Номер телефона должен начинаться с +7 или 8.")
        if len(value) != 12 and len(value) != 11:
            raise serializers.ValidationError("Номер телефона должен содержать 11 цифр (9XXXXXXXXX).")
        if not value[1:].isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры после кода страны.")
        return value

    def validate_unique_token(self, value):
        try:
            offer = Offer.objects.get(unique_token=value)
        except Offer.DoesNotExist:
            raise serializers.ValidationError("Оффер с таким токеном не найден.")
        return value

    def create(self, validated_data):
        offer = Offer.objects.get(unique_token=validated_data['unique_token'])

        # Проверка на уникальность номера для оффера
        if LeadWall.objects.filter(phone=validated_data['phone'], offer=offer).exists():
            raise serializers.ValidationError("Лид с таким номером телефона уже существует для данного оффера.")

        # Обработка статуса оффера
        if offer.status == 'registered':
            offer.status = 'active'
            offer.save()
        elif offer.status in ['paused', 'stopped']:
            offer, created = Offer.objects.get_or_create(name='AdStart', defaults={'status': 'active'})

        lead = LeadWall.objects.create(
            offer=offer,
            name=validated_data['name'],
            phone=validated_data['phone'],
            status='new'
        )
        return lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadWall
        fields = ['id', 'name', 'phone', 'description', 'status', 'offer', 'created_at']
        read_only_fields = ['id', 'created_at']


class LeadUpdateSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=LeadWall.LEAD_STATUS_CHOICES)
