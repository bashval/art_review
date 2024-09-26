from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import USER_ROLE_LENGTH, EMAIL_LENGTH


class Users(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
        (USER, 'user')
    )

    email = models.EmailField(
        'Адрес электронной почты', max_length=EMAIL_LENGTH, unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=USER_ROLE_LENGTH, choices=ROLES, default=USER
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
