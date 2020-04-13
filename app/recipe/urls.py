from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views

# The DefaultRouter auto generates the urls for a viewset.
# One viewset may have multiple urls.
router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)
# So the reverse function may find
app_name = 'recipe'

urlpatterns = [
    # router.urls NOT a str
    path('', include(router.urls)),
]
