from typing import Type

from django.db.models import Model
from django.shortcuts import get_object_or_404


def get_object_by_pk(model: Type[Model], key_name: str, kwargs: dict):
    obj_id = kwargs.get(key_name)
    obj = get_object_or_404(model, pk=obj_id)
    return obj
