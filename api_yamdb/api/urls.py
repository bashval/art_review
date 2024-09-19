from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('v1/auth/token', TokenObtainPairView.as_view()),
]
