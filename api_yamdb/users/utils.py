from django.core.mail import send_mail

from api_yamdb.settings import CONFIRMATION_EMAIL


def send_confirmation_mail(email, code):
    send_mail(
        subject='Confirmation Code',
        message=code,
        from_email=CONFIRMATION_EMAIL,
        recipient_list=[email],
        fail_silently=True
    )
