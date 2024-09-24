from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .permissions import IsOwnerOrStaffOrReadOnly


class CreateListDestroyViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class ReviewCommentMixin:
    permission_classes = (IsOwnerOrStaffOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
