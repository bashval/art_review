from typing import Any, Type, Union

from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404


def get_object_by_pk(
        model: Union[Type[Model], QuerySet], kwargs: dict, **key_names: Any
):
    for key, value in key_names.items():
        key_names[key] = kwargs.get(value)
    obj = get_object_or_404(model, **key_names)
    return obj
