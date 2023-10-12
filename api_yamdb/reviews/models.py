import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
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


class Title(models.Model):
    pass


class Category(models.Model):
    pass


class Genre(models.Model):
    pass


class Reviews(models.Model):
    """Модель отзыва на произведение"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название произведения',
        help_text='Выберите произведение, к которому относится этот отзыв.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='reviews',
        verbose_name='Автор отзыва',
        help_text='Выберите автора этого отзыва.'
    )
    text = models.CharField(
        max_length=400,
        verbose_name='Текст отзыва',
        help_text='Введите текст отзыва (необязательно).'
    )
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(limit_value=1),
            MaxValueValidator(limit_value=10),
        ],
        null=False,
        blank=False,
        verbose_name='Оценка произведения',
        help_text='Введите оценку произведения от 1 до 10.'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата размещения',
        help_text='Дата и время размещения этого отзыва.'
    )

    class Meta:
        verbose_name = 'Отзыв на произведение'
        verbose_name_plural = 'Отзывы на произведение'
        ordering = ('pub_date',)

    def __str__(self) -> str:
        return f'Отзыв {self.author} на {self.title}'


class Comments(models.Model):
    """Модель комментариев к отзывам"""
    review = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв на произведение',
        help_text='Выбор отзыва',
    )
    text = models.CharField(
        max_length=150,
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата размещения комментария',
        help_text='Дата и время размещения этого комментария.'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий к отзыву'
        verbose_name_plural = 'Комментарии к отзыву'

    def __str__(self) -> str:
        return self.text
