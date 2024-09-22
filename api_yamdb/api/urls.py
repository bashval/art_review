from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet
from users.views import (
    UserForAdminViewSet,
    user_signup_view,
    obtain_token_view
)

router_v1 = DefaultRouter()
router_v1.register(r'users', UserForAdminViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    (r'titles/(?P<title_pk>\d+)/reviews/(?P<review_pk>\d+)/'
     r'comments/(?P<comment_pk>\d+)$'),
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
