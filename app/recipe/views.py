from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers


# Gone use only list mixin. There are update, delete mixins ...
class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin, mixins.CreateModelMixin):
    # Requires that Token atuth is used and user is auth.
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # ListModeMixin requires a queryset set
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # When TagViewSet/ListModelMixin is involked, the get_queryset function is
    # called to retrieve the objects
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Overrride teh perform_create function and create a new tag with an
        auth user"""
        # When create is invoked, perform_create is called, received serialiser
        # as arg, so one can customize teh creation: set the user to the auth
        # user.
        serializer.save(user=self.request.user)
