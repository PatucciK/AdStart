# views.py
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import AdvertiserSerializer, WebmasterSerializer

class CreateAdvertiserAPIView(APIView):
    @swagger_auto_schema(
        request_body=AdvertiserSerializer,
        operation_description="Создать нового рекламодателя. Необязательные поля могут быть пропущены. Требуется аутентификация администратора.",
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин администратора",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль администратора",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            201: "Рекламодатель успешно создан.",
            400: "Ошибка валидации данных.",
            401: "Неверные учетные данные или недостаточно прав."
        },
        tags=['Создание пользователей'],
        operation_summary="Создание нового рекламодателя"
    )
    def post(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)

        if not user or not user.is_superuser:
            return Response({"detail": "Неверные учетные данные или недостаточно прав."},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = AdvertiserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Рекламодатель успешно создан."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateWebmasterAPIView(APIView):
    @swagger_auto_schema(
        request_body=WebmasterSerializer,
        operation_description="Создать нового вебмастера. Необязательные поля могут быть пропущены. Требуется аутентификация администратора.",
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин администратора",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль администратора",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            201: "Вебмастер успешно создан.",
            400: "Ошибка валидации данных.",
            401: "Неверные учетные данные или недостаточно прав."
        },
        tags=['Создание пользователей'],
        operation_summary="Создание нового вебмастера"
    )
    def post(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)

        if not user or not user.is_superuser:
            return Response({"detail": "Неверные учетные данные или недостаточно прав."},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = WebmasterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Вебмастер успешно создан."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
