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

    @property
    def is_admin(self):
        return self.is_staff or self.role == settings.ADMIN

    @property
    def is_moderator(self):
        return self.role == settings.MODERATOR


class Category(models.Model):
    """ Модель категории произведения"""
    name = models.CharField(
        blank=False,
        default='Category',
        max_length=256
    )
    slug = models.SlugField(
        blank=False,
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    """ Модель жанра произведения"""
    name = models.CharField(
        blank=False,
        default='Genre',
        max_length=256
    )
    slug = models.SlugField(
        blank=False,
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    """ Модель произведения"""
    name = models.CharField(
        blank=False,
        max_length=256
    )
    year = models.IntegerField(
        blank=False
    )
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre,
        blank=False
    )
    category = models.ForeignKey(
        Category,
        blank=False,
        on_delete=models.CASCADE,
        related_name='titles'
    )
    rating = models.FloatField(
        blank=False,
        default=0
    )

    def __str__(self):
        return self.name
