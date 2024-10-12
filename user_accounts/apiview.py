from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .serializers import AdvertiserSerializer, WebmasterSerializer
from .models import EmailConfirmation, Webmaster, Advertiser
import random
import string


# Генерация JWT токенов
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


# Отправка кода подтверждения на email
def send_confirmation_email(email, confirmation_code):
    send_mail(
        'Подтверждение email',
        f'Ваш код подтверждения: {confirmation_code}',
        'from@example.com',
        [email],
        fail_silently=False,
    )


# Создание нового пользователя (Advertiser/Webmaster)
def create_user_account(user_type, data):
    if user_type == 'advertiser':
        serializer = AdvertiserSerializer(data=data)
    elif user_type == 'webmaster':
        serializer = WebmasterSerializer(data=data)
    else:
        return None, {"message": "Неверный тип пользователя."}

    if serializer.is_valid():
        user = serializer.save()
        return user, None
    return None, serializer.errors


# API для подтверждения email и регистрации пользователя
class ConfirmEmailAndRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Подтверждение email и регистрация пользователя.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email для подтверждения кода', example='user@example.com'),
                'confirmation_code': openapi.Schema(type=openapi.TYPE_STRING, description='Код подтверждения', example='123456'),
                'user_type': openapi.Schema(type=openapi.TYPE_STRING, description='Тип пользователя ("advertiser" или "webmaster")', example='advertiser'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль для учетной записи', example='your_password'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя', example='john_doe'),
                'telegram': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID', example='@mytelegram'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона', example='79991234567'),
            },
            required=['email', 'confirmation_code', 'user_type', 'password', 'username'],
        ),
        responses={
            201: openapi.Response('Email confirmed and account created successfully.'),
            400: openapi.Response('Invalid data or confirmation code.'),
            404: openapi.Response('Email not found.')
        },
        operation_summary="Подтверждение email и регистрация пользователя.",
        tags=['Rest User']  # Добавлен тег
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')
        user_type = request.data.get('user_type')
        password = request.data.get('password')
        username = request.data.get('username')

        # Проверка обязательных полей
        if not all([email, confirmation_code, user_type, password, username]):
            return Response({"message": "Все обязательные поля должны быть заполнены."}, status=status.HTTP_400_BAD_REQUEST)

        # Поиск подтверждения email
        try:
            email_confirmation = EmailConfirmation.objects.get(email=email)
        except EmailConfirmation.DoesNotExist:
            return Response({"message": "Email не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Проверка кода подтверждения
        if email_confirmation.confirmation_code != confirmation_code:
            return Response({"message": "Неверный код подтверждения."}, status=status.HTTP_400_BAD_REQUEST)

        if email_confirmation.is_expired():
            return Response({"message": "Код подтверждения истек."}, status=status.HTTP_400_BAD_REQUEST)

        # Подтверждение email
        email_confirmation.is_confirmed = True
        email_confirmation.save()

        # Создаем пользователя с указанными данными
        user_data = {
            'user': {
                'username': username,
                'email': email,
                'password': password
            },
            'telegram': request.data.get('telegram', ''),
            'phone': request.data.get('phone', '')
        }

        # Создание пользователя в зависимости от типа
        if user_type == 'advertiser':
            serializer = AdvertiserSerializer(data=user_data)
        elif user_type == 'webmaster':
            serializer = WebmasterSerializer(data=user_data)
        else:
            return Response({"message": "Неверный тип пользователя."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            user = serializer.save()

            # Генерация JWT токенов
            tokens = get_tokens_for_user(user.user)

            return Response({
                "message": "Email подтвержден и аккаунт успешно создан.",
                "tokens": tokens
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API для создания рекламодателя
class CreateAdvertiserAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Только аутентифицированные пользователи могут создавать рекламодателя

    @swagger_auto_schema(
        operation_description="Создать нового рекламодателя. Необязательные поля могут быть пропущены.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя', example='john_doe'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя', example='advertiser@example.com'),
                'telegram': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID', example='@mytelegram'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона', example='79991234567'),
            },
            required=['username', 'email'],
        ),
        responses={
            201: openapi.Response('Рекламодатель успешно создан.'),
            400: openapi.Response('Ошибка валидации данных.'),
        },
        operation_summary="Создание рекламодателя.",
        tags=['Rest User']  # Добавлен тег
    )
    def post(self, request, *args, **kwargs):
        serializer = AdvertiserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Рекламодатель успешно создан."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API для создания вебмастера
class CreateWebmasterAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Только аутентифицированные пользователи могут создавать вебмастера

    @swagger_auto_schema(
        operation_description="Создать нового вебмастера. Необязательные поля могут быть пропущены.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя', example='webmaster_doe'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя', example='webmaster@example.com'),
                'telegram': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID', example='@mytelegram'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона', example='79991234567'),
                'experience': openapi.Schema(type=openapi.TYPE_STRING, description='Опыт вебмастера', example='3 года опыта в сфере IT'),
                'stats_screenshot': openapi.Schema(type=openapi.TYPE_STRING, description='Ссылка на скриншот статистики', example='http://example.com/screenshot.png'),
            },
            required=['username', 'email'],
        ),
        responses={
            201: openapi.Response('Вебмастер успешно создан.'),
            400: openapi.Response('Ошибка валидации данных.'),
        },
        operation_summary="Создание вебмастера.",
        tags=['Rest User']  # Добавлен тег
    )
    def post(self, request, *args, **kwargs):
        serializer = WebmasterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Вебмастер успешно создан."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API для запроса кода подтверждения по email
class RequestConfirmationCodeAPIView(APIView):
    permission_classes = [AllowAny]  # Любой пользователь может запросить код подтверждения

    @swagger_auto_schema(
        operation_description="Запросить код подтверждения на email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email для отправки кода подтверждения', example='user@example.com'),
            },
            required=['email'],
        ),
        responses={
            200: openapi.Response('Confirmation code sent to email.'),
            400: openapi.Response('Invalid email.')
        },
        operation_summary="Запросить код подтверждения по email.",
        tags=['Rest User']  # Добавлен тег
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Генерация случайного кода подтверждения
        confirmation_code = ''.join(random.choices(string.digits, k=6))

        # Обновление или создание записи для подтверждения
        EmailConfirmation.objects.update_or_create(
            email=email,
            defaults={'confirmation_code': confirmation_code, 'is_confirmed': False}
        )

        # Отправка email с кодом подтверждения
        send_confirmation_email(email, confirmation_code)

        return Response({"message": "Confirmation code sent to email."}, status=status.HTTP_200_OK)


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Пользователь может обновить данные только если он владелец аккаунта
    или имеет флаг персонала (staff).
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ, если пользователь является владельцем аккаунта или имеет статус staff
        return obj.user == request.user or request.user.is_staff

# Обновление данных рекламодателя
class UpdateAdvertiserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]  # Только владелец или персонал может обновлять

    @swagger_auto_schema(
        operation_description="Обновить данные рекламодателя. Доступно только владельцу или пользователю с правами персонала.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'telegram': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID', example='@newtelegram'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона', example='79991234567'),
            },
        ),
        responses={
            200: openapi.Response('Данные рекламодателя успешно обновлены.'),
            400: openapi.Response('Ошибка валидации данных.'),
            403: openapi.Response('Доступ запрещен.'),
        },
        operation_summary="Обновление данных рекламодателя.",
        tags=['Rest User']  # Тег для документации Swagger
    )
    def patch(self, request, *args, **kwargs):
        try:
            advertiser = Advertiser.objects.get(user=request.user)
        except Advertiser.DoesNotExist:
            return Response({"detail": "Рекламодатель не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем права на обновление
        self.check_object_permissions(request, advertiser)

        serializer = AdvertiserSerializer(advertiser, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Данные рекламодателя успешно обновлены."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Обновление данных вебмастера
class UpdateWebmasterAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]  # Только владелец или персонал может обновлять

    @swagger_auto_schema(
        operation_description="Обновить данные вебмастера. Доступно только владельцу или пользователю с правами персонала.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'telegram': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID', example='@newtelegram'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона', example='79991234567'),
                'experience': openapi.Schema(type=openapi.TYPE_STRING, description='Опыт вебмастера', example='4 года опыта в сфере IT'),
                'stats_screenshot': openapi.Schema(type=openapi.TYPE_STRING, description='Ссылка на новый скриншот', example='http://example.com/screenshot.png'),
            },
        ),
        responses={
            200: openapi.Response('Данные вебмастера успешно обновлены.'),
            400: openapi.Response('Ошибка валидации данных.'),
            403: openapi.Response('Доступ запрещен.'),
        },
        operation_summary="Обновление данных вебмастера.",
        tags=['Rest User']  # Тег для документации Swagger
    )
    def patch(self, request, *args, **kwargs):
        try:
            webmaster = Webmaster.objects.get(user=request.user)
        except Webmaster.DoesNotExist:
            return Response({"detail": "Вебмастер не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем права на обновление
        self.check_object_permissions(request, webmaster)

        serializer = WebmasterSerializer(webmaster, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Данные вебмастера успешно обновлены."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)