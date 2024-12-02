# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/root/data/www/faq-reg.ru/project_name')
sys.path.insert(1, '/var/www/python3.12/data/djangoenv/lib/python3.7/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'AdStart.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()