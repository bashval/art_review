from typing import Any, Type, Union

from django.core.mail import send_mail
from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404

from api_yamdb.settings import CONFIRMATION_EMAIL


def get_object_by_pk(
        model: Union[Type[Model], QuerySet], kwargs: dict, **key_names: Any
):
    for key, value in key_names.items():
        key_names[key] = kwargs.get(value)
    obj = get_object_or_404(model, **key_names)
    return obj


def send_confirmation_mail(email, code):
    send_mail(
        subject='Confirmation Code',
        message=code,
        from_email=CONFIRMATION_EMAIL,
        recipient_list=[email],
        fail_silently=True
    )
