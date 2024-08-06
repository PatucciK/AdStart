from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import LeadWall
from .serializers import LeadWallSerializer, LeadUpdateSerializer, LeadSerializer


class LeadWallAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]  # Защита от спама

    @swagger_auto_schema(
        operation_description="Принимает лидов с проверкой и обработкой статусов офферов",
        request_body=LeadWallSerializer,
        responses={
            201: openapi.Response(
                description="Лид успешно создан.",
                examples={
                    'application/json': {
                        "detail": "Лид успешно создан."
                    }
                }
            ),
            400: openapi.Response(
                description="Ошибка валидации данных.",
                examples={
                    'application/json': {
                        "phone": ["Номер телефона должен начинаться с +7 или 8."],
                        "unique_token": ["Оффер с таким токеном не найден."],
                        "non_field_errors": ["Лид с таким номером телефона уже существует для данного оффера."]
                    }
                }
            ),
            429: openapi.Response(
                description="Превышено ограничение скорости запросов.",
                examples={
                    'application/json': {
                        "detail": "Request was throttled. Expected available in 60 seconds."
                    }
                }
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера.",
                examples={
                    'application/json': {
                        "detail": "Произошла внутренняя ошибка сервера."
                    }
                }
            )
        },
        tags=['Leads'],
        operation_summary="Создание нового лида",
        examples={
            'application/json': {
                "unique_token": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Иван Иванов",
                "phone": "+79991234567"
            }
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Метод для обработки создания нового лида.

        **Описание:**
        - Проверяет уникальность номера телефона для оффера.
        - Переводит статус оффера в "Активен", если он был "Регистрация".
        - Создает или использует оффер "AdStart", если текущий оффер в статусе "Пауза" или "СТОП".

        **Примечание:** Защита от спама реализована через ограничение скорости запросов.
        """
        serializer = LeadWallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Лид успешно создан."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadListView(APIView):
    @swagger_auto_schema(
        operation_description="Получить все лиды по логину и паролю рекламодателя",
        responses={200: LeadSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя",
                              type=openapi.TYPE_STRING),
        ],
        tags=['Leads'],
        operation_summary="Получение всех лидов рекламодателя"
    )
    def get(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)
            if advertiser is not None:
                leads = LeadWall.objects.filter(offer__partner_card__advertiser=advertiser)
                serializer = LeadSerializer(leads, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Рекламодатель не найден."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)


class LeadUpdateView(APIView):
    @swagger_auto_schema(
        operation_description="Обновить статус лида по логину и паролю рекламодателя",
        request_body=LeadUpdateSerializer,
        responses={200: "Статус успешно обновлен."},
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя",
                              type=openapi.TYPE_STRING),
        ],
        tags=['Leads'],
        operation_summary="Обновление статуса лида"
    )
    def put(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)
            if advertiser is not None:
                serializer = LeadUpdateSerializer(data=request.data)
                if serializer.is_valid():
                    lead_id = serializer.validated_data['lead_id']
                    new_status = serializer.validated_data['status']

                    lead = LeadWall.objects.filter(id=lead_id, offer__partner_card__advertiser=advertiser).first()
                    if lead:
                        if lead.can_change_to(new_status):
                            lead.status = new_status
                            lead.save()
                            return Response({"detail": "Статус успешно обновлен."}, status=status.HTTP_200_OK)
                        return Response({"detail": "Нельзя изменить на этот статус."},
                                        status=status.HTTP_400_BAD_REQUEST)
                    return Response({"detail": "Лид не найден или недоступен."}, status=status.HTTP_404_NOT_FOUND)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Рекламодатель не найден."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)