from datetime import datetime

from rest_framework import serializers

from reviews.constants import MAX_SCORE, MIN_SCORE
from reviews.models import (
    Category,
    Genre,
    Title,
    Comment,
    Review
)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для чтения."""

    rating = serializers.IntegerField(required=False, allow_null=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:

        fields = '__all__'
        model = Title

    def validate_year(self, value):
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Это поле не может быть пустым.'
            )
        return value


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для Create, Update и Delete."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:

        fields = '__all__'
        model = Title


class CustomDefault:
    requires_context = True

    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, serializer_field):
        obj = serializer_field.context.get(self.key_name)
        return obj


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=CustomDefault('title'))

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='Можно написать только один отзыв к тайтлу'
            ),
        )

    def validate_score(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                'Оценка тайтлу должна быть целым числом'
            )

        if not (MIN_SCORE <= value <= MAX_SCORE):
            message = f'Оценка должна быть от {MIN_SCORE} до {MAX_SCORE}'
            raise serializers.ValidationError(message)
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    review = serializers.HiddenField(default=CustomDefault('review'))

    class Meta:
        model = Comment
        fields = ('id', 'text', 'pub_date', 'author', 'review')
