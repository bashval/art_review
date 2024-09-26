from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import IsAdmin
from .serializers import (
    UserSerializer,
    UserSignupSerializer,
    TokenObtainSerializer
)
from .utils import send_confirmation_mail


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup_view(request):
    serializer = UserSignupSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    if not (request.user.is_authenticated and request.user.is_admin):
        email = serializer.validated_data.get('email')
        code = default_token_generator.make_token(serializer.instance)
        send_confirmation_mail(email, code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token_view(request):
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = User.objects.get(
        username=serializer.validated_data.get('username')
    )
    access_token = AccessToken.for_user(user)
    return Response({'token': str(access_token)})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_value_regex = r'[\w/./@/+/-]+'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
    )
    def user_update_his_data(self, request):
        if request.method == 'PATCH':
            serializer = self.serializer_class(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
