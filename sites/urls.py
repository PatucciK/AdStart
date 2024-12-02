from django.urls import path
from .views import upload_archive, view_site, download_archive

urlpatterns = [
    path('upload/', upload_archive, name='upload_archive'),
    path('view/<slug:category_slug>/<slug:site_slug>/<path:path>', view_site, name='view_file'),
    path('view/<slug:category_slug>/<slug:site_slug>', view_site, name='view_file'),
    path('download/<str:unique_token>/<slug:category_slug>/<slug:site_slug>/', download_archive, name='download_archive'),
]

