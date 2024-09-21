from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import filters, viewsets
from reviews.models import Category, Genre, Title

from .filters import TitleFilter
from .mixins import CreateListDestroyViewset
#from .permissions import ()
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleCreateSerializer, TitleReadSerializer)


class GenreViewSet(CreateListDestroyViewset):
    """Вью-класс для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    #permission_classes = 
    #pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewset):
    """Вью-класс для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = "slug"
    #permission_classes = 
    #pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleCreateSerializer
    #permission_classes =
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    #pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleReadSerializer
