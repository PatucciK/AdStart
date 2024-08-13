# AdStart/urls.py
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from offers.apiview import LeadWallAPIView, LeadListView, LeadUpdateView, OfferListView, OfferCreateView, \
    OfferUpdateView
from partner_cards.apiview import CreatePartnerCardAPIView
from user_accounts.apiview import CreateAdvertiserAPIView, CreateWebmasterAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="AdStart API",
        default_version='0.1',
        description="Документация для API приёма лидов (POST /api/leads/)",
        contact=openapi.Contact(email="caramba.piy@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def redirect_to_profile(request):
    return redirect('/accounts/profile/')


urlpatterns = [
    path('', redirect_to_profile),
    path('admin/', admin.site.urls),
    path('accounts/', include('user_accounts.urls')),
    path('content/', include('content.urls')),
    path('partner_cards/', include('partner_cards.urls')),
    path('offers/', include('offers.urls')),
]

# API
urlpatterns += [
    path('api/leads/', LeadWallAPIView.as_view(), name='leadwall-api'),
    path('api/docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/leads_list/', LeadListView.as_view(), name='lead_list'),
    path('api/leads/update/', LeadUpdateView.as_view(), name='lead_update'),
    path('api/create-advertiser/', CreateAdvertiserAPIView.as_view(), name='create-advertiser'),
    path('api/create-webmaster/', CreateWebmasterAPIView.as_view(), name='create-webmaster'),
    path('api/create-partner-card/', CreatePartnerCardAPIView.as_view(), name='create-partner-card'),
    path('api/offers/', OfferListView.as_view(), name='offer-list'),
    path('api/offers/create/', OfferCreateView.as_view(), name='offer-create'),
    path('api/offers/<int:offer_id>/update/', OfferUpdateView.as_view(), name='offer-update')

]
