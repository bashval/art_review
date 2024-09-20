from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Title(models.Model):
    pass


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикаций', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, message='Оценка не должна быть меньше 1'),
            MaxValueValidator(10, message='Оценка не должна быть больше 10')
        ]
    )
    title_id = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )

    class Meta:
        contraints = (
            models.UniqueConstraint(
                fields=('author', 'title_id'),
                name='Один отзыв от автора для одного тайтла'
            ),
        )
