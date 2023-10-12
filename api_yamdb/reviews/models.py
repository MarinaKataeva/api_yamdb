import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class User(AbstractUser):

    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
    )
    confirmation_code = models.UUIDField(
        'Код для получения и обновления токена',
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    bio = models.TextField(
        'О себе',
        blank=True,
    )
    role = models.CharField(
        'Пользовательская роль',
        max_length=24,
        choices=CHOICES,
        default='user',
    )

    class Meta:
        ordering = ['id']

    @property
    def is_admin(self):
        return self.is_staff or self.role == settings.ADMIN

    @property
    def is_moderator(self):
        return self.role == settings.MODERATOR
