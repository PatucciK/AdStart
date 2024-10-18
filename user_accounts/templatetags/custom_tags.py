import requests
from django import template
from user_accounts.models import Advertiser, Webmaster
from offers.models import OfferWebmaster, Offer
from django.shortcuts import get_object_or_404

register = template.Library()


@register.inclusion_tag('user_accounts/menu.html', takes_context=True)
def load_menu(context):
    user = context['user']
    advertiser_profile = None
    webmaster_profile = None

    if user.is_authenticated:
        try:
            advertiser_profile = Advertiser.objects.get(user=user)
        except Advertiser.DoesNotExist:
            pass

        try:
            webmaster_profile = Webmaster.objects.get(user=user)
        except Webmaster.DoesNotExist:
            pass

    return {
        'user': user,
        'advertiser_profile': advertiser_profile,
        'webmaster_profile': webmaster_profile,
    }


@register.filter
def get_geolocation(ip):
    try:
        response = requests.get(f'http://ipinfo.io/{ip}/json')
        data = response.json()
        return f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
    except Exception:
        return "Unknown Location"

@register.simple_tag(takes_context=True)
def is_mine(context, offer_id):
    # Пример простой функции, которая принимает значение и возвращает результат
    offer = get_object_or_404(Offer, id=int(offer_id))
    webmaster = get_object_or_404(Webmaster, user=context['request'].user)
    # Проверка, что связь еще не создана
    if not OfferWebmaster.objects.filter(offer=offer, webmaster=webmaster).exists():
        return False
    return True