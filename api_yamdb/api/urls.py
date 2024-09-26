from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    CommentViewSet,
    ReviewViewSet
)
from users.views import (
    UserViewSet,
    user_signup_view,
    obtain_token_view
)


router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet)
router_v1.register('titles', TitleViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register(r'users', UserViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    (r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments'),
    CommentViewSet,
    basename='comments'
)

api_v1 = [
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path("v1/auth/signup/", user_signup_view, name="signup"),
    path('v1/auth/token/', obtain_token_view, name='token'),
    path('v1/', include(api_v1)),
]
