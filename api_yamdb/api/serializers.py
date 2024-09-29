from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.constants import MAX_SCORE, MIN_SCORE
from reviews.models import (
    Category,
    Genre,
    Title,
    Comment,
    Review
)
from users.constants import USERNAME_LENGTH
from .utils import get_object_by_pk

User = get_user_model()


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


class TitleBase(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )


class TitleReadSerializer(TitleBase):
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='slug',
    )
    genre = GenreSerializer(many=True)


class TitleCreateSerializer(TitleBase):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True)
    description = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['genre'] = GenreSerializer(
            Genre.objects.filter(slug__in=ret['genre']),
            many=True
        ).data
        ret['category'] = CategorySerializer(
            Category.objects.get(slug=ret['category'])
        ).data
        return ret

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


class TitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        request = serializer_field.context.get('request')
        title = get_object_by_pk(Title,
                                 request.parser_context['kwargs'],
                                 pk='title_id')
        return title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=TitleDefault())
    score = serializers.IntegerField(min_value=MIN_SCORE, max_value=MAX_SCORE)

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


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'pub_date', 'author')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Данное имя не доступно для регистрации.'
            )
        return value


class UserSignupSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')

    def run_validation(self, data):
        username = data.get('username')
        email = data.get('email')
        if user := User.objects.filter(username=username, email=email).first():
            self.instance = user
        return super().run_validation(data)


class TokenObtainSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.RegexField(
        regex=UnicodeUsernameValidator.regex,
        max_length=USERNAME_LENGTH,
        required=True
    )

    def validate(self, data):
        user = get_object_or_404(User, username=data.get('username'))
        if not default_token_generator.check_token(
            user, data.get('confirmation_code')
        ):
            raise serializers.ValidationError(
                'Неверный код подтверждения'
            )
        return data
