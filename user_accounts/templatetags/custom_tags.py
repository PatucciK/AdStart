from django import template
from user_accounts.models import Advertiser, Webmaster

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
