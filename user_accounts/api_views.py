from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail
from .serializers import AdvertiserSerializer, WebmasterSerializer
from .models import EmailConfirmation
import random
import string


class RequestConfirmationCodeAPIView(APIView):
    """
    Запрос кода подтверждения по email.

    Параметры:
    - email: Email для отправки кода подтверждения (обязательно)

    Ответ:
    - message: Сообщение о результате запроса
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Запрос кода подтверждения по email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email для отправки кода подтверждения'),
            },
            required=['email'],
        ),
        responses={
            200: openapi.Response('Confirmation code sent to email.'),
            400: openapi.Response('Invalid email.')
        },
        operation_summary="Запрос кода подтверждения по email.",
        tags=['Регистрация'],
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        confirmation_code = ''.join(random.choices(string.digits, k=6))
        EmailConfirmation.objects.update_or_create(
            email=email,
            defaults={'confirmation_code': confirmation_code, 'is_confirmed': False}
        )

        send_mail(
            'Подтверждение email',
            f'Ваш код подтверждения: {confirmation_code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        return Response({"message": "Confirmation code sent to email."}, status=status.HTTP_200_OK)


class ConfirmEmailAndRegisterAPIView(APIView):
    """
    Подтверждение email с помощью кода и регистрация пользователя.

    Параметры:
    - email: Email, для которого нужно подтвердить код (обязательно)
    - confirmation_code: Код подтверждения, полученный по email (обязательно)
    - user_type: Тип пользователя ('advertiser' или 'webmaster') (обязательно)
    - password: Пароль для учетной записи (обязательно)
    - telegram: Telegram ID или URL профиля (необязательно)
    - phone: Номер телефона в формате 10 цифр без +7 (необязательно)

    Ответ:
    - message: Сообщение о результате подтверждения и создания аккаунта
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Подтверждение email с помощью кода и регистрация пользователя.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email для подтверждения кода'),
                'confirmation_code': openapi.Schema(type=openapi.TYPE_STRING,
                                                    description='Код подтверждения, полученный по email'),
                'user_type': openapi.Schema(type=openapi.TYPE_STRING,
                                            description='Тип пользователя ("advertiser" или "webmaster")'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль для учетной записи'),
                'telegram': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID или URL профиля'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Номер телефона в формате 10 цифр без +7'),
            },
            required=['email', 'confirmation_code', 'user_type', 'password'],
        ),
        responses={
            201: openapi.Response('Email confirmed and account created successfully.'),
            400: openapi.Response('Invalid data or confirmation code.'),
            404: openapi.Response('Email not found.')
        },
        operation_summary="Подтверждение email с помощью кода и регистрация пользователя и внесение информации о "
                          "пользователе в базу данных.",
        tags=['Регистрация']
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')
        user_type = request.data.get('user_type')

        if not email or not confirmation_code or not user_type:
            return Response({"message": "Email, confirmation code and user type are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            email_confirmation = EmailConfirmation.objects.get(email=email)
            if email_confirmation.confirmation_code == confirmation_code:
                if email_confirmation.is_expired():
                    return Response({"message": "Confirmation code has expired."}, status=status.HTTP_400_BAD_REQUEST)

                email_confirmation.is_confirmed = True
                email_confirmation.save()

                if user_type == 'advertiser':
                    serializer = AdvertiserSerializer(data=request.data)
                elif user_type == 'webmaster':
                    serializer = WebmasterSerializer(data=request.data)
                else:
                    return Response({"message": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

                if serializer.is_valid():
                    user = serializer.save()
                    return Response({"message": "Email confirmed and account created successfully."},
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)
        except EmailConfirmation.DoesNotExist:
            return Response({"message": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
