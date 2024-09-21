from django.urls import include, path
from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    # MyTokenObtainPairView,
    UserForAdminViewSet,
    UserSignupAPIView,
    user_update_himself,
    user_signup_view,
    obtain_token_view
)


router_v1 = DefaultRouter()
router_v1.register(r'users', UserForAdminViewSet)

urlpatterns = [
    # path('v1/auth/signup/', UserSignupAPIView.as_view()),
    path("v1/auth/signup/", user_signup_view, name="signup"),
    # path('v1/auth/token/', TokenObtainPairView.as_view()),
    path('v1/auth/token/', obtain_token_view, name='token'),
    path('v1/users/me/', user_update_himself),
    # path(r'^v1/users/(?P<username>[\w/./@/+/-]+)$', UserForAdminViewSet.as_view()),
    path('v1/', include(router_v1.urls)),
]
