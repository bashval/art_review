from collections import OrderedDict
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
from users.constants import EMAIL_LENGTH, USERNAME_LENGTH
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


class TitleCreateSlugField(serializers.SlugRelatedField):

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


class TitleCreateSerializer(TitleBase):
    category = TitleCreateSlugField(
        queryset=Category.objects.all(),
        slug_field='slug',
        represent_field=('name', 'slug')
    )
    genre = TitleCreateSlugField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        represent_field=('name', 'slug'),
        allow_null=False
    )
    description = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False, allow_null=True)

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


class BaseUserSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Данное имя не доступно для регистрации.'
            )
        return value


class UserSerializer(BaseUserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserSignupSerializer(BaseUserSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_LENGTH,
    )
    username = serializers.RegexField(
        regex=UnicodeUsernameValidator.regex,
        max_length=USERNAME_LENGTH,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if user := User.objects.filter(username=username, email=email).first():
            self.instance = user
            return data
        if (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            raise serializers.ValidationError(
                'Пользователь с таким имем/почтой уже существует.'
            )
        return data


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
