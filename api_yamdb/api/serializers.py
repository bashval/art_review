from typing import Any, Dict
from django.contrib.auth import get_user_model
from rest_framework import serializers, validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        return super().validate(attrs)


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


class UserSignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')
        extra_kwargs = {'email': {'required': True}}

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Данное имя не доступно для регистрации.'
            )
        return value

    def validate_email(self, value):
        if len(value) > 250:
            raise serializers.ValidationError(
                'Убедитесь, что это значение содержит не более 254 символов.'
            )
        return value
