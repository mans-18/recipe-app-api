from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


# For the detail URL, we need arg in a function to pass to a url
def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """ Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


# ** means any additional param off user will get passed as a dic named params
def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    # No need to pass user to the default dic because it passed evey single
    # the def sample_recipe is called
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # Any params passed in off the user will override the default
    defaults.update(params)

    # ** here converts the dic into the args
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe api access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is requeired"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test auth recipe api access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@ufc.br',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        # Error: Positional args follow kw args
        # sample_recipe(user=self.user, {
        #    'title': '',
        #    'time_minutes': 10,
        #    'price': 5.00
        # })
        # sample_recipe(user=self.user, {
        #    'title': '',
        #    'time_minutes': 20,
        #    'price': 10.00
        # })
        # ##### Accepted this one. Lets see!!! #######
        # sample_recipe({
        #    'title': 'Fried fish',
        #    'time_minutes': 10,
        #    'price': 5.00
        # TypeError: sample_recipe() got multiple values for argument 'user'
        # }, user=self.user)
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # If don't order_by('-id'), no error: AssertionError: [OrderedDict
        # ([('id', 4), ('title', 'Sample recipe'), ('time_mi[221 chars]])])] !=
        # [OrderedDict([('id', 5), ('title', 'Sample recipe'), ('time_mi[221
        # chars]])])]
        # recipes = Recipe.objects.all().order_by('-id')
        recipes = Recipe.objects.all().order_by('price')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for auth user only"""
        user2 = get_user_model().objects.create_user(
            'other@ufc.br',
            'pasrd'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail with related objects"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
