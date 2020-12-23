from core.models import Recipe, Tag, Ingredient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
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


def sample_tag(user, name="Main Tag"):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Garlic"):
    return Ingredient.objects.create(user=user, name=name)


def detail_url(recupe_id):
    """RETURN THE RECIPE DETAILS URK"""
    return reverse('recipe:recipe-detail', args=[recupe_id])


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

    def test_recipe_view_details(self):
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

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
