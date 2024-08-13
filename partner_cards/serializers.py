# serializers.py
from rest_framework import serializers
from .models import PartnerCard

class PartnerCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerCard
        fields = [
            'advertiser', 'logo', 'name', 'legal_name', 'license',
            'website', 'legal_address', 'actual_addresses', 'company_details',
            'contracts', 'main_phone', 'deposit', 'is_approved'
        ]

        # Указываем, что некоторые поля могут быть пустыми
        extra_kwargs = {
            'logo': {'required': False},
            'license': {'required': False},
            'company_details': {'required': False},
            'contracts': {'required': False},
            'deposit': {'required': False, 'default': 0},
        }
