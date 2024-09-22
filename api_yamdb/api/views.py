from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyViewset, ReviewCommentMixin
from .permissions import IsOwnerOrStaffOrReadOnly
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
    #permission_classes = 
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewset):
    """Вью-класс для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = "slug"
    #permission_classes = 
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleCreateSerializer
    #permission_classes =
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleReadSerializer


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
