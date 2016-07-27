#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

gunicorn --bind 0.0.0.0:$PORT app.wsgi
