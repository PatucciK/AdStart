from django.urls import path
from . import views, api_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register/advertiser/', views.register_advertiser, name='register_advertiser'),
    path('register/webmaster/', views.register_webmaster, name='register_webmaster'),
    path('confirm_email/<str:email>/', views.confirm_email, name='confirm_email'),
    path('confirm_email_webmaster/<str:email>/', views.confirm_email_webmaster, name='confirm_email_webmaster'),
    path('api/request-confirmation-code/', api_views.RequestConfirmationCodeAPIView.as_view(), name='request_confirmation_code'),
    path('api/confirm-email/', api_views.ConfirmEmailAndRegisterAPIView.as_view(), name='confirm_email_and_register'),
]
