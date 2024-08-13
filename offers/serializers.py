from rest_framework import serializers
from .models import Offer, LeadWall, OfferWebmaster

class LeadWallSerializer(serializers.Serializer):
    unique_token = serializers.UUIDField(required=True, help_text="Уникальный токен оффера для идентификации")
    name = serializers.CharField(max_length=255, required=True, help_text="Имя пользователя, отправляющего лид")
    phone = serializers.CharField(max_length=15, required=True,
                                  help_text="Номер телефона пользователя в формате +7XXXXXXXXXX или 8XXXXXXXXXX")
    description = serializers.CharField(max_length=500, required=False, allow_blank=True,
                                        help_text="Описание лида (необязательно)")

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
            offer_webmaster = OfferWebmaster.objects.get(unique_token=value)
        except OfferWebmaster.DoesNotExist:
            raise serializers.ValidationError("Оффер с таким токеном не найден.")
        return value

    def create(self, validated_data):
        offer_webmaster = OfferWebmaster.objects.get(unique_token=validated_data['unique_token'])

        # Проверка на уникальность номера для оффера
        if LeadWall.objects.filter(phone=validated_data['phone'], offer_webmaster=offer_webmaster).exists():
            raise serializers.ValidationError("Лид с таким номером телефона уже существует для данного оффера.")

        description = validated_data.get('description', '')
        # Добавляем "[Создан через API]" к описанию
        full_description = f"[Создан через API] {description}" if description else "[Создан через API]"

        lead = LeadWall.objects.create(
            offer_webmaster=offer_webmaster,
            name=validated_data['name'],
            phone=validated_data['phone'],
            description=full_description,
            processing_status='new'
        )
        return lead

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadWall
        fields = ['id', 'name', 'phone', 'description', 'status', 'processing_status', 'offer_webmaster', 'created_at']
        read_only_fields = ['id', 'created_at']

class LeadUpdateSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    processing_status = serializers.ChoiceField(choices=LeadWall.PROCESSING_STATUS_CHOICES)


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            'id', 'partner_card', 'logo', 'name', 'inn', 'contract_number',
            'contract_date', 'working_hours', 'service_description',
            'geo', 'lead_price', 'status', 'public_status'
        ]
        read_only_fields = ['id', 'partner_card', 'status', 'contract_number']

class OfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            'logo', 'name', 'inn', 'contract_date', 'working_hours',
            'service_description', 'geo', 'lead_price', 'public_status'
        ]

    def validate(self, data):
        if data.get('public_status') == 'public' and not data.get('lead_price'):
            raise serializers.ValidationError("Цена за лид обязательна для публичного оффера.")
        elif data.get('public_status') == 'private' and data.get('lead_price') is not None:
            raise serializers.ValidationError("Цена за лид не должна указываться для закрытого оффера.")
        return data

class OfferUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['status']

