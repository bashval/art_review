from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import CategoryGenreMixin, ReviewCommentMixin
from .permissions import IsAdminOrReadOnly, IsAdmin
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleCreateSerializer,
    TokenObtainSerializer,
    UserSerializer,
    UserSignupSerializer
)
from .utils import get_object_by_pk, send_confirmation_mail

User = get_user_model()


class GenreViewSet(CategoryGenreMixin):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreMixin):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')
    ordering = ('name', 'id')

    def get_serializer_class(self):
        if self.action == 'get':
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(ReviewCommentMixin, viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer

    @property
    def get_title(self):
        title = get_object_by_pk(Title, self.kwargs, pk='title_id')
        return title

    def get_queryset(self):
        reviews = self.get_title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title)


class CommentViewSet(ReviewCommentMixin, viewsets.ModelViewSet):
    """Вьюсет для комментарии."""

    serializer_class = CommentSerializer

    @property
    def get_review(self):
        review = get_object_by_pk(
            Review, self.kwargs, pk='review_id', title__id='title_id'
        )
        return review

    def get_queryset(self):
        comments = self.get_review.comments.all()
        return comments

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review)


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
