from rest_framework import mixins, viewsets


class CreateListDestroyViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass
