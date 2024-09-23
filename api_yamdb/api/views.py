from django.db.models import Avg

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyViewset, ReviewCommentMixin
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleCreateSerializer,
    TitleReadSerializer,
    CommentSerializer,
    ReviewSerializer
)
from .utils import get_object_by_pk


class GenreViewSet(CreateListDestroyViewset):
    """Вью-класс для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewset):
    """Вью-класс для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleCreateSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleReadSerializer


class ReviewViewSet(ReviewCommentMixin, viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        reviews = title.reviews.all().order_by('id', 'pub_date')
        return reviews

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title'] = get_object_by_pk(Title, 'title_id', self.kwargs)
        return context


class CommentViewSet(ReviewCommentMixin, viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_review(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        review = get_object_by_pk(
            title.reviews.all(), 'review_id', self.kwargs
        )
        return review

    def get_queryset(self):
        review = self.get_review()
        comments = review.comments.all().order_by('id', 'pub_date')
        return comments

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['review'] = self.get_review()
        return context
