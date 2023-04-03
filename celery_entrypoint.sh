#!/bin/sh

celery -A order_service worker -l info

exec "$@"