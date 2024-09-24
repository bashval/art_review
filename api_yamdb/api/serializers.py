from collections import OrderedDict
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


class CustomSlugField(serializers.SlugRelatedField):

    def __init__(self, represent_field=None, **kwargs):
        assert represent_field is not None, (
            'The `represent_field` argument is required.'
        )
        self.represent_field = represent_field
        super().__init__(**kwargs)

    def to_representation(self, obj):
        ret = OrderedDict()
        fields = self.represent_field

        for field in fields:
            value = getattr(obj, field)
            ret[field] = value
        return ret


class TitleSerializer(serializers.ModelSerializer):
    category = CustomSlugField(
        queryset=Category.objects.all(),
        slug_field='slug',
        represent_field=('name', 'slug')
    )
    genre = CustomSlugField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        represent_field=('name', 'slug'),
        allow_null=False
    )
    description = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )

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
