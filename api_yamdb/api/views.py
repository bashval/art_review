from rest_framework import mixins, viewsets

from .methods import get_object_by_pk
from .mixins import PartialUpdateModelMixin
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrStaffOrReadOnly
from .serializers import ReviewSerializer

from reviews.models import Review, Title


class ReviewViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
    mixins.DestroyModelMixin, PartialUpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrStaffOrReadOnly,)

    def get_queryset(self):
        # Тут использую собственный метод,
        # чтобы придерживаться DRY, как мне сказал
        # сделать мой ревьюер
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        reviews = title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        serializer.save(author=self.request.user, title_id=title)
