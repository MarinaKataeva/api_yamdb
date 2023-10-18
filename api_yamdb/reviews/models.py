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
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category_titles'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genre_titles',
        through='GenreTitle'
    )
    rating = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
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
        null=False,
        blank=False,
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
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review'
            )
        ]

    def __str__(self) -> str:
        return f'Отзыв {self.author} на {self.title}'


class Comment(models.Model):
    """Модель комментариев к отзывам"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв на произведение',
        help_text='Выбор отзыва',
    )
    text = models.CharField(
        max_length=150,
        null=False,
        blank=False,
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
