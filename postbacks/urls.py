# postbacks/urls
from django.urls import path
from .apiviews import Postback

urlpatterns = [
    path('postback1', Postback.as_view(), name="Постбэк 1")
]