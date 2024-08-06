# AdStart/urls.py
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from offers.apiview import LeadWallAPIView, LeadListView, LeadUpdateView

schema_view = get_schema_view(
    openapi.Info(
        title="Lead API",
        default_version='v1',
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
]
