from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import IsAdmin
from .serializers import UserForHimselfSerializer, UserSerializer, UserSignupSerializer

from .utils import get_object_by_pk
from .mixins import ReviewCommentMixin
from .permissions import IsAdmin, IsOwnerOrStaffOrReadOnly
from .serializers import CommentSerializer, ReviewSerializer, TokenObtainSerializer

from reviews.models import Title


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
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    try:
        user, _ = User.objects.get_or_create(username=username, email=email)
    except IntegrityError:
        return Response(
            'Something wrong',
            status=status.HTTP_400_BAD_REQUEST
        )
    if not (request.user.is_authenticated and request.user.role == User.ADMIN):
        code = default_token_generator.make_token(user)
        send_confirmatio_mail(email, code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token_view(request):
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            'Something wrong',
            status=status.HTTP_400_BAD_REQUEST
        )
    access_token = AccessToken.for_user(user)
    return Response({'token': str(access_token)})


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


class ReviewViewSet(ReviewCommentMixin, viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrStaffOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        reviews = title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        serializer.save(author=self.request.user, title_id=title)


class CommentViewSet(ReviewCommentMixin, viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrStaffOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_review(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        review = get_object_by_pk(
            title.reviews.all(), 'review_id', self.kwargs
        )

        return review

    def get_queryset(self):
        review = self.get_review()
        comments = review.comments.all()
        return comments

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review_id=review)
