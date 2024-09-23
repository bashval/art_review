from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import USER_ROLE_LENGTH


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    MODERTOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'admin'),
        (MODERTOR, 'moderator'),
        (USER, 'user')
    )

    email = models.EmailField(
        'Адрес электронной почты', max_length=254, unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=USER_ROLE_LENGTH, choices=ROLES, default=USER
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
