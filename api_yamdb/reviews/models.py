from django.contrib.auth import get_user_model
from django.db import models


class Genre(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=200)
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=200,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=200)
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=200,
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

    name = models.CharField(verbose_name='Произведение', max_length=80)
    year = models.SmallIntegerField(verbose_name='Год выпуска',) # Подсмотрел у Санжара в модели валидатор MaxValueValidator, можно воткнуть чтобы дату больше чем сегодняшняя не поставить
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

    # "rating =" возможно нужно будет для реализации отображения рейтинга произведения

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
    ...


class Comment(models.Model):
    ...
