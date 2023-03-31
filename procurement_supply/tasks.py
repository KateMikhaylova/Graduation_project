from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task()
def send_email(title, message, address):
    send_mail(title, message, settings.EMAIL_HOST_USER, address, fail_silently=False)
