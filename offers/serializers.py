from rest_framework import serializers
from .models import Offer, LeadWall, OfferWebmaster, Click


class LeadWallSerializer(serializers.Serializer):
    unique_token = serializers.UUIDField(required=True, help_text="Уникальный токен оффера для идентификации")
    name = serializers.CharField(max_length=255, required=False, help_text="Имя пользователя, отправляющего лид")
    phone = serializers.CharField(max_length=15, required=True,
                                  help_text="Номер телефона пользователя в формате +7XXXXXXXXXX или 8XXXXXXXXXX")
    description = serializers.CharField(max_length=500, required=False, allow_blank=True,
                                        help_text="Описание лида (необязательно)")
    q1 = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="Дополнительный вопрос 1")
    q2 = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="Дополнительный вопрос 2")
    q3 = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="Дополнительный вопрос 3")
    q4 = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="Дополнительный вопрос 4")
    q5 = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="Дополнительный вопрос 5")
    sub_1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    sub_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    sub_3 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    sub_4 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    sub_5 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    ip_adress = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text="IP-адрес отправителя")
    domain = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text="Доменное имя отправителя")

    def validate_phone(self, value):
        if not (value.startswith('+7') or value.startswith('8')):
            raise serializers.ValidationError("Номер телефона должен начинаться с +7 или 8.")
        if len(value) not in (11, 12):
            raise serializers.ValidationError("Номер телефона должен содержать 11 цифр (9XXXXXXXXX).")
        if not value[1:].isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры после кода страны.")
        return value

    def validate_unique_token(self, value):
        try:
            OfferWebmaster.objects.get(unique_token=value)
        except OfferWebmaster.DoesNotExist:
            raise serializers.ValidationError("Оффер с таким токеном не найден.")
        return value

    def create(self, validated_data):
        offer_webmaster = OfferWebmaster.objects.get(unique_token=validated_data['unique_token'])

        # Проверка на уникальность номера для оффера
        if LeadWall.objects.filter(phone=validated_data['phone'], offer_webmaster=offer_webmaster).exists():
            raise serializers.ValidationError("Лид с таким номером телефона уже существует для данного оффера.")

        description = validated_data.get('description', '')
        description_extra = ", ".join(filter(None, [validated_data.get(f'q{i}') for i in range(1, 6)]))

        lead = LeadWall.objects.create(
            offer_webmaster=offer_webmaster,
            name=validated_data['name'],
            phone=validated_data['phone'],
            description=f"[Создан через API] {description}" if description else "[Создан через API]",
            description_extra=description_extra,
            sub_1=validated_data.get('sub_1'),
            sub_2=validated_data.get('sub_2'),
            sub_3=validated_data.get('sub_3'),
            sub_4=validated_data.get('sub_4'),
            sub_5=validated_data.get('sub_5'),
            processing_status='new'
        )
        return lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadWall
        fields = ['id', 'name', 'phone', 'description', 'description_extra', 'status', 'processing_status',
                  'offer_webmaster', 'created_at']
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

class OfferDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"

class ClickSerializer(serializers.Serializer):
    unique_token = serializers.UUIDField(required=True, help_text="Уникальный токен оффера для идентификации")
    click_data = serializers.CharField(required=False, allow_blank=True, help_text="Данные о клиенте")
    sub_1 = serializers.CharField(required=False, allow_blank=True, help_text="Sub 1")
    sub_2 = serializers.CharField(required=False, allow_blank=True, help_text="Sub 2")
    sub_3 = serializers.CharField(required=False, allow_blank=True, help_text="Sub 3")
    sub_4 = serializers.CharField(required=False, allow_blank=True, help_text="Sub 4")
    sub_5 = serializers.CharField(required=False, allow_blank=True, help_text="Sub 5")
    ip_address = serializers.CharField(required=False, allow_blank=True, help_text="IP-адрес отправителя")
    domain = serializers.CharField(required=False, allow_blank=True, help_text="Домен отправителя")

    def validate_unique_token(self, value):
        try:
            OfferWebmaster.objects.get(unique_token=value)
        except OfferWebmaster.DoesNotExist:
            raise serializers.ValidationError("Оффер с таким токеном не найден.")
        return value

    def create(self, validated_data):
        offer_webmaster = OfferWebmaster.objects.get(unique_token=validated_data['unique_token'])
        click = Click.objects.create(
            offer_webmaster=offer_webmaster,
            click_data=validated_data.get('click_data', ''),
            ip_adress=validated_data.get('ip_address', ''),
            domain=validated_data.get('domain', ''),
            sub_1=validated_data.get('sub_1', ''),
            sub_2=validated_data.get('sub_2', ''),
            sub_3=validated_data.get('sub_3', ''),
            sub_4=validated_data.get('sub_4', ''),
            sub_5=validated_data.get('sub_5', ''),
        )
        return click
