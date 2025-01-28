# ats/serializers
from rest_framework import serializers
from .models import CallBegin
from django.contrib.auth.models import User

class CallBeginSerializer(serializers.ModelSerializer):

    # number_a = serializers.CharField(source="client_number")
    number_a = serializers.CharField(source="client_number")
    client = serializers.IntegerField(required=False)
    redirect_number = serializers.CharField(source="manager_number")
    manager = serializers.IntegerField(required=False)
    date_time = serializers.DateTimeField(source="created_at")

    class Meta:
        model = CallBegin
        fields = [
            "number_a",
            "redirect_number",
            "date_time",
            "client",
            "manager",
        ]

    def create(self, validated_data):
        # client_phone = validated_data.get("client_number", None)
        # manager_phone = validated_data.get("manager_number", None)

        # try:
        #     validated_data['client'] = User.objects.get(phone=client_phone)
        # except User.DoesNotExist:
        #     pass
        # try:
        #     validated_data['manager'] = User.objects.get(phone=manager_phone)
        # except User.DoesNotExist:
        #     pass

        return CallBegin.objects.create(**validated_data)