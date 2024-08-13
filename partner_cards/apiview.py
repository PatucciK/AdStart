# views.py
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import PartnerCardSerializer


class CreatePartnerCardAPIView(APIView):
    @swagger_auto_schema(
        request_body=PartnerCardSerializer,
        operation_description="Создать новую карточку партнера. Необязательные поля могут быть пропущены. Требуется аутентификация администратора.",
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин администратора",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль администратора",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            201: "Карточка партнера успешно создана.",
            400: "Ошибка валидации данных.",
            401: "Неверные учетные данные или недостаточно прав."
        },
        tags=['Создание пользователей'],
        operation_summary="Создание новой карточки партнера"
    )
    def post(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)

        if not user or not user.is_superuser:
            return Response({"detail": "Неверные учетные данные или недостаточно прав."},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = PartnerCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Карточка партнера успешно создана."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
