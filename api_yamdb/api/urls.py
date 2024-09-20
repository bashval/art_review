from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet

router = DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)

api_v1 = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('v1/', include(api_v1)),
]
