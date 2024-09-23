from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from reviews.models import (
    Category,
    Genre,
    Title,
    Comment,
    Review
)
from reviews.constants import MAX_SCORE, MIN_SCORE


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


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(
        read_only=True
    )
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        title = get_object_or_404(Title, pk=obj.id)
        reviews_score = (title
                         .reviews.all()
                         .aggregate(Avg('score'))
                         .get('score__avg'))
        if reviews_score:
            return int(reviews_score)
        return


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
