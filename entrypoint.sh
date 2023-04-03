#!/bin/sh

sleep 10

python manage.py makemigrations
python manage.py makemigrations procurement_supply
python manage.py migrate
python manage.py createcachetable


if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL \
        --first_name $DJANGO_SUPERUSER_NAME \
        --last_name $DJANGO_SUPERUSER_SURNAME \
        --company $DJANGO_SUPERUSER_COMPANY \
        --position $DJANGO_SUPERUSER_POSITION


gunicorn order_service.wsgi:application --bind 0.0.0.0:8000
fi
exec "$@"
