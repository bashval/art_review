from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user.role == User.ADMIN
                     or request.user.is_superuser))
        )


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user == obj.author
                     or request.user.role == User.ADMIN
                     or request.user.role == User.MODERATOR
                     or request.user.is_superuser))
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated
                    and (request.user.role == User.ADMIN
                         or request.user.is_superuser))
