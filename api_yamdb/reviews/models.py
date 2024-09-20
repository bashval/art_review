from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Title(models.Model):
    pass


class Review(models.Model):
    '''Модель отзывов.'''

    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField('Дата публикаций', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Автор'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, message='Оценка не должна быть меньше 1'),
            MaxValueValidator(10, message='Оценка не должна быть больше 10')
        ],
        verbose_name='Оценка'
    )
    title_id = models.ForeignKey(
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


class Comment(models.Model):
    '''Модель комментариев.'''

    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор'
    )
    review_id = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Ревью'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
