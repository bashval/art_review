# from typing import Any, Dict
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers, validators

from reviews.models import Comment, Review

User = get_user_model()


class TokenObtainSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserPostSerializer(UserSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )


class UserForHimselfSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        regex=UnicodeUsernameValidator.regex,
        max_length=150, required=True
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Данное имя не доступно для регистрации.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title_id')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title_id'),
                message='Можно написать только один отзыв к тайтлу'
            ),
        )
        read_only_fields = ('title_id',)

    def validate_score(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                'Оценка тайтлу должна быть целым числом'
            )

        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10')

        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('title_id', None)
        return representation


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'pub_date', 'author', 'review_id')
        read_only_fields = ('review_id',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('review_id', None)
        return representation
