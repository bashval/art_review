from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyViewset, ReviewCommentMixin
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    CommentSerializer,
    ReviewSerializer
)
from .utils import get_object_by_pk


class GenreViewSet(CreateListDestroyViewset):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewset):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')
    ordering = ('name', 'id')


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
