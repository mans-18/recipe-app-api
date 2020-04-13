from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


# Gone use only list mixin. There are update, delete mixins ...
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    # Case viewset for user owned recipe attr
    # Requires that Token atuth is used and user is auth.
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # When ViewSet/ListModelMixin is involked, the get_queryset function is
    # called to retrieve the objects
    def get_queryset(self):
        """Return objects for current auth user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # When create is invoked, perform_create is called, receives serializer
    # as arg, so one can customize the creation: set the user to the auth
    # user.
    def perform_create(self, serializer):
        """Override the perform_create function and create a new obj for
        an auth user only"""
        # Atention to the arg of save(). 'user' is in the request
        serializer.save(user=self.request.user)


# Gone use only list mixin. There are update, delete mixins ...
class TagViewSet(BaseRecipeAttrViewSet):
    # ListModeMixin requires a queryset set
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


# If This view does not exists and it is not registered on the urls.py,
# the error occurs: 'django.urls.exceptions.NoReverseMatch: Reverse for
# 'ingredient-list' not found. 'ingredient-list' is not a valid view function
# or pattern name'
class IngredientViewSet(BaseRecipeAttrViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the db"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the recipes for the auth user only"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)
