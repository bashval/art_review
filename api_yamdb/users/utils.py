from django.core.mail import send_mail


def send_confirmatio_mail(email, code):
    send_mail(
        subject='Confirmation Code',
        message=code,
        from_email='from@dummy-mail.com',
        recipient_list=[email],
        fail_silently=True
    )
