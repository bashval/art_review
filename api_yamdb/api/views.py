from rest_framework import pagination, viewsets

from .methods import get_object_by_pk
from .mixins import ReviewCommentMixin
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrStaffOrReadOnly
from .serializers import CommentSerializer, ReviewSerializer

from reviews.models import Title


class ReviewViewSet(ReviewCommentMixin, viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrStaffOrReadOnly,)
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        reviews = title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        serializer.save(author=self.request.user, title_id=title)


class CommentViewSet(ReviewCommentMixin, viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrStaffOrReadOnly,)
    pagination_class = pagination.PageNumberPagination

    def get_review(self):
        title = get_object_by_pk(Title, 'title_id', self.kwargs)
        review = get_object_by_pk(
            title.reviews.all(), 'review_id', self.kwargs
        )

        return review

    def get_queryset(self):
        review = self.get_review()
        comments = review.comments.all()
        return comments

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review_id=review)
