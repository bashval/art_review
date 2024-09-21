from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import IsAdmin
from .serializers import UserForHimselfSerializer, UserPostSerializer, UserSerializer, UserSignupSerializer

User = get_user_model()


def send_confirmatio_mail(email, code):
    send_mail(
        subject='Confirmation Code',
        message=code,
        from_email='from@dummy-mail.com',
        recipient_list=[email],
        fail_silently=True
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup_view(request):
    serializer = UserSignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    if not User.objects.filter(username=username, email=email).exists():
        serializer.save()
    if not (request.user.is_authenticated and request.user.role == User.ADMIN):
        code = '31428'
        send_confirmatio_mail(email, code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token_view(request):
    user = get_object_or_404(User, username=request.data.get('username'))
    access_token = AccessToken.for_user(user=user)
    return Response({'token': str(access_token)})


class UserSignupAPIView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        confirmation_code = '31428'
        send_mail(
            subject='Confirmation Code',
            message=confirmation_code,
            from_email='from@dummy-mail.com',
            recipient_list=[request.data.get('email')],
            fail_silently=True
        )
        return response


class UserForAdminViewSet(
    generics.ListCreateAPIView,
    generics.RetrieveUpdateDestroyAPIView,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_value_regex = r'[\w/./@/+/-]+'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserPostSerializer
        return super().get_serializer_class()


@api_view(['GET', 'PATCH'])
def user_update_himself(request):
    user = request.user
    if request.method == 'PATCH':
        serializer = UserForHimselfSerializer(user, data=request.data, partial=True)
        print(serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# class UserForHimselfViewSet(generics.RetrieveUpdateAPIView):
#     serializer_class = UserForHimselfSerializer
#     permission_classes = [IsUserItself]

#     def get_queryset(self):
#         return self.request.user
