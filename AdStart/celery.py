from celery import Celery, shared_task
from celery.schedules import crontab
from django.conf import settings
from django.core.mail import send_mail
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AdStart.settings')

app = Celery('AdStart')

app.config_from_object('django.conf:settings')

# Убедитесь, что задачи автоматически находятся

app.autodiscover_tasks(['offers'])


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     from offers.tasks import check_for_repository_updates
#
#     sender.add_periodic_task(
#         crontab(hour="0", minute="5"),
#         check_for_repository_updates.s(),
#     )


@shared_task
def send_verification_email_async(to_email, code):
    send_mail(
        'Подтверждение регистрации',
        f'Ваш код подтверждения: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
