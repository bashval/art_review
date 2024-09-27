from django.db.models import Avg

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets, exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyViewset, ReviewCommentMixin
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleReadSerializer,
    CommentSerializer,
    ReviewSerializer
)
from .utils import get_object_by_pk


class GenreViewSet(CreateListDestroyViewset):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewset):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
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
    ordering = ('name', 'id')

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return TitleReadSerializer
        return TitleSerializer

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ReviewViewSet(ReviewCommentMixin, viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        reviews = title.reviews.all().order_by('-pub_date', 'id')
        return reviews

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title'] = get_object_by_pk(Title, 'title_id', self.kwargs)
        return context


class CommentViewSet(ReviewCommentMixin, viewsets.ModelViewSet):
    """Вьюсет для комментарии."""

    serializer_class = CommentSerializer

    def get_review(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        review = get_object_by_pk(
            title.reviews.all(), 'review_id', self.kwargs
        )
        return review

    def get_queryset(self):
        review = self.get_review()
        comments = review.comments.all().order_by('-pub_date', 'id')
        return comments

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['review'] = self.get_review()
        return context
