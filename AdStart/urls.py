from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from offers.apiview import LeadWallAPIView, LeadListView, LeadUpdateView, OfferListView, OfferCreateView, \
    OfferUpdateView, ClickAPIView, OfferDeleteView
from partner_cards.apiview import CreatePartnerCardAPIView
from user_accounts.apiview import CreateAdvertiserAPIView, CreateWebmasterAPIView, RequestConfirmationCodeAPIView, \
    ConfirmEmailAndRegisterAPIView, UpdateAdvertiserAPIView, UpdateWebmasterAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Schema for swagger and redoc
schema_view = get_schema_view(
    openapi.Info(
        title="AdStart API",
        default_version='0.1',
        description="Документация для API",
        contact=openapi.Contact(email="caramba.piy@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def redirect_to_profile(request):
    return redirect('/accounts/profile/')


urlpatterns = [
    # Admin and user redirects
    path('', redirect_to_profile),
    path('admin/', admin.site.urls),

    # Include apps' URLs
    path('accounts/', include('user_accounts.urls')),
    path('content/', include('content.urls')),
    path('partner_cards/', include('partner_cards.urls')),
    path('offers/', include('offers.urls')),
    path('sites/', include('sites.urls')),

    # API documentation
    path('api/docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Leads API
    path('api/leads/', LeadWallAPIView.as_view(), name='leadwall-api'),
    path('api/leads_list/', LeadListView.as_view(), name='lead_list'),
    path('api/leads/update/', LeadUpdateView.as_view(), name='lead_update'),
    path('api/leads/click', ClickAPIView.as_view(), name='offer-click-create'),

    # Offers API
    path('api/offers/', OfferListView.as_view(), name='offer-list'),
    path('api/offers/create/', OfferCreateView.as_view(), name='offer-create'),
    path('api/offers/<int:offer_id>/update/', OfferUpdateView.as_view(), name='offer-update'),
    path('api/offers/<int:offer_id>/delete/', OfferDeleteView.as_view(), name='offer-delete'),

    # User creation APIs (Advertiser and Webmaster)
    path('api/create-advertiser/', CreateAdvertiserAPIView.as_view(), name='create-advertiser'),
    path('api/create-webmaster/', CreateWebmasterAPIView.as_view(), name='create-webmaster'),

    # Partner card API
    path('api/create-partner-card/', CreatePartnerCardAPIView.as_view(), name='create-partner-card'),

    # Email confirmation and registration APIs
    path('api/request-confirmation-code/', RequestConfirmationCodeAPIView.as_view(), name='request-confirmation-code'),
    path('api/confirm-email-and-register/', ConfirmEmailAndRegisterAPIView.as_view(),
         name='confirm-email-and-register'),
    path('api/advertiser/update/', UpdateAdvertiserAPIView.as_view(), name='update-advertiser'),
    path('api/webmaster/update/', UpdateWebmasterAPIView.as_view(), name='update-webmaster'),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Add media URL serving in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
