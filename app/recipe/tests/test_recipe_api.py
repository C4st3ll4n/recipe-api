from core.models import Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPE_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 10,
        "price": 5.0
    }

    defaults.update(**params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    """TEST THE PUBLIC ENDPOINTS"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "teste@recipe.com",
            'recipetestpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retireve_recipes_success(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user, title="second recipe")

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_add_recipe_success(self):
        pass

    def test_add_recipe_invalid(self):
        pass

    def test_recipe_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            "other@teste.com",
            'testzineo'
        )

        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
