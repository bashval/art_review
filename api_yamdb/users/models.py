from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
        (USER, 'user')
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Роль', max_length=16, choices=ROLES, default=USER)
    confirmation_code = models.CharField('Код подтверждения', max_length=12)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
