from celery import Celery
from celery.schedules import crontab
from django.conf import settings

app = Celery('AdStart')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Убедитесь, что задачи автоматически находятся
app.autodiscover_tasks(['offers'])  # Указываем приложение с задачами


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from offers.tasks import check_for_repository_updates

    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        check_for_repository_updates.s(),
    )
