from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet)


router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)

api_v1 = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('v1/', include(api_v1)),
]