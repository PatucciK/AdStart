#!/bin/bash
set -a; . .env.prod;
python manage.py runserver 0.0.0.0:8000