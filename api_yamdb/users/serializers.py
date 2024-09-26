from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from .constants import EMAIL_LENGTH, USERNAME_LENGTH


User = get_user_model()


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
