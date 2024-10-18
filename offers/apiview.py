from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import LeadWall, Offer
from .serializers import LeadWallSerializer, LeadUpdateSerializer, LeadSerializer, OfferUpdateSerializer, \
    OfferCreateSerializer, OfferSerializer, ClickSerializer, OfferDeleteSerializer


class LeadWallAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Принимает лидов с проверкой и обработкой статусов офферов",
        request_body=LeadWallSerializer,
        responses={
            201: openapi.Response(description="Лид успешно создан."),
            400: openapi.Response(description="Ошибка валидации данных."),
            429: openapi.Response(description="Превышено ограничение скорости запросов."),
            500: openapi.Response(description="Внутренняя ошибка сервера.")
        },
        tags=['Лиды'],
        operation_summary="Создание нового лида"
    )
    def post(self, request, *args, **kwargs):
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
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя", type=openapi.TYPE_STRING),
        ],
        tags=['Лиды'],
        operation_summary="Получение всех лидов рекламодателя"
    )
    def get(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)
            if advertiser:
                leads = LeadWall.objects.filter(offer_webmaster__offer__partner_card__advertiser=advertiser)
                serializer = LeadSerializer(leads, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Рекламодатель не найден."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)



class LeadUpdateView(APIView):
    @swagger_auto_schema(
        operation_description="Обновить статус обработки лида по логину и паролю рекламодателя",
        request_body=LeadUpdateSerializer,
        responses={200: openapi.Response(
            description="Статус успешно обновлен.",
            examples={'application/json': {"detail": "Статус успешно обновлен.", "status": "paid"}}
        )},
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя", type=openapi.TYPE_STRING),
        ],
        tags=['Лиды'],
        operation_summary="Обновление статуса обработки лида"
    )
    def put(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)
            if advertiser:
                serializer = LeadUpdateSerializer(data=request.data)
                if serializer.is_valid():
                    lead_id = serializer.validated_data['lead_id']
                    new_processing_status = serializer.validated_data['processing_status']

                    lead = LeadWall.objects.filter(id=lead_id, offer_webmaster__offer__partner_card__advertiser=advertiser).first()
                    if lead and lead.processing_status in ['new', 'no_response']:
                        lead.processing_status = new_processing_status

                        if new_processing_status in ['callback', 'appointment', 'visit']:
                            lead.status = 'paid'
                            lead.offer_webmaster.offer.partner_card.deposit -= lead.offer_webmaster.offer.lead_price
                            lead.offer_webmaster.offer.partner_card.save()
                        elif new_processing_status == 'rejected':
                            lead.status = 'cancelled'

                        lead.save()
                        return Response({"detail": "Статус успешно обновлен.", "status": lead.status}, status=status.HTTP_200_OK)
                    return Response({"detail": "Лид не найден или нельзя изменить на этот статус."}, status=status.HTTP_404_NOT_FOUND)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Рекламодатель не найден."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)


class OfferListView(APIView):
    @swagger_auto_schema(
        operation_description="Получить все офферы по логину и паролю рекламодателя",
        responses={200: OfferSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя", type=openapi.TYPE_STRING),
        ],
        tags=['Офферы'],
        operation_summary="Получение всех офферов рекламодателя"
    )
    def get(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)
            if advertiser is not None:
                offers = Offer.objects.filter(partner_card__advertiser=advertiser)
                serializer = OfferSerializer(offers, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Рекламодатель не найден."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)

class OfferCreateView(APIView):
    @swagger_auto_schema(
        request_body=OfferCreateSerializer,
        operation_description="Создать новый оффер. Необязательные поля могут быть пропущены.",
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя", type=openapi.TYPE_STRING),
        ],
        responses={
            201: "Оффер успешно создан.",
            400: "Ошибка валидации данных.",
            401: "Неверные учетные данные или недостаточно прав."
        },
        tags=['Офферы'],
        operation_summary="Создание нового оффера"
    )
    def post(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)
            if advertiser is not None and advertiser.partner_card:
                serializer = OfferCreateSerializer(data=request.data)
                if serializer.is_valid():
                    offer = serializer.save(partner_card=advertiser.partner_card, status='registered')
                    return Response({"detail": "Оффер успешно создан.", "offer_id": offer.id}, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "У рекламодателя нет партнерской карты."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)

class OfferUpdateView(APIView):
    @swagger_auto_schema(
        request_body=OfferUpdateSerializer,
        operation_description="Обновить статус оффера по логину и паролю рекламодателя",
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя", type=openapi.TYPE_STRING),
            openapi.Parameter('offer_id', openapi.IN_PATH, description="ID оффера", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: "Статус оффера успешно обновлен.",
            400: "Ошибка валидации данных.",
            401: "Неверные учетные данные или недостаточно прав."
        },
        tags=['Офферы'],
        operation_summary="Обновление статуса оффера"
    )
    def put(self, request, offer_id, *args, **kwargs):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)
            if advertiser is not None:
                offer = Offer.objects.filter(id=offer_id, partner_card__advertiser=advertiser).first()
                if offer:
                    serializer = OfferUpdateSerializer(offer, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({"detail": "Статус оффера успешно обновлен."}, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response({"detail": "Оффер не найден или недоступен."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)

class OfferDeleteView(APIView):
    @swagger_auto_schema(
        request_body=OfferDeleteSerializer,
        operation_description="Удалить оффер",
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Логин рекламодателя",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Пароль рекламодателя",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('offer_id', openapi.IN_PATH, description="ID оффера", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: "Статус оффера успешно удален.",
            400: "Ошибка валидации данных.",
            401: "Неверные учетные данные или недостаточно прав."
        },
        tags=['Офферы'],
        operation_summary="Удаление оффера"
    )

    def delete(self, request, offer_id, *args, **kwargs):
        username = request.query_params.get('username')
        password = request.query_params.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.is_authenticated:
            advertiser = getattr(user, 'advertiser', None)

            if advertiser is not None:
                offer = Offer.objects.filter(id=offer_id, partner_card__advertiser=advertiser).first()
                if offer:
                    offer.delete()
                    return Response({"detail": "Статус оффера успешно удален."}, status=status.HTTP_200_OK)
                return Response({"detail": "Оффер не найден или недоступен."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)

class ClickAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Создание нового клика",
        request_body=ClickSerializer,
        responses={
            201: openapi.Response(description="Клик успешно создан."),
            400: openapi.Response(description="Ошибка валидации данных."),
            429: openapi.Response(description="Превышено ограничение скорости запросов."),
            500: openapi.Response(description="Внутренняя ошибка сервера.")
        },
        tags=['Лиды'],
        operation_summary="Создание нового клика"
    )
    def post(self, request, *args, **kwargs):
        serializer = ClickSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Клик успешно создан."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)