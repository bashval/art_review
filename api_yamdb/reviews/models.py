from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .constants import NAME_LENGTH, SLUG_LENGTH, MAX_SCORE, MIN_SCORE

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Наименование', max_length=NAME_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=SLUG_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=256)
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=SLUG_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведение."""

    name = models.CharField(
        verbose_name='Произведение', max_length=NAME_LENGTH
    )
    year = models.SmallIntegerField(verbose_name='Год выпуска',)
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Вспомогательная модель жанров произведения."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр',
    )

    class Meta:
        """Мета класс жанров произведения."""

        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведения'

    def __str__(self):
        """Описание жанров произведения."""
        return f'{self.title}, {self.genre}'


class Review(models.Model):
    """Модель отзывов."""

    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикаций', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Автор'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(
                MIN_SCORE, message=f'Оценка не должна быть меньше {MIN_SCORE}'
            ),
            MaxValueValidator(
                MAX_SCORE, message=f'Оценка не должна быть больше {MAX_SCORE}'
            )
        ],
        verbose_name='Оценка'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Произведение'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title_id'),
                name='unique_review_author_for_one_title'
            ),
        )

    def __str__(self):
        """Описание отзывов произведения."""

        return f'Отзыв об {self.title.name} от {self.author.username}'


class Comment(models.Model):
    """Модель комментариев."""

    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата комментария', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Ревью'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Описание комментариев произведения."""

        return f'Комментарий отзыва {self.review.title.name}'
