from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator

from rest_framework import serializers


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


class TokenObtainSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.RegexField(
        regex=UnicodeUsernameValidator.regex,
        max_length=150, required=True
    )

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSignupSerializer(BaseUserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')
