from core.models import Ingredient, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import IngredientSerializer
from rest_framework import status
from rest_framework.test import APIClient

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """TEST ENDPOINTS FOR AUTHORIZED USERS"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'teste@gmail.com',
            'teste4password'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """TEST THAT ONLY INGREDIENTS FOR
        THE AUTHENTICATED USER ARE RETURNED"""

        user = get_user_model().objects.create_user(
            "user@teste.com",
            "teste2pass"
        )

        Ingredient.objects.create(user=user, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="Garlic")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_sucessful(self):
        ingredient_payload = {"name": "Cabbage"}
        res = self.client.post(INGREDIENTS_URL, ingredient_payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=ingredient_payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        ingredient_payload = {"name": ""}
        res = self.client.post(INGREDIENTS_URL, ingredient_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredient_assigned_to_recipe(self):
        ingredient1 = Ingredient.objects.create(
            user=self.user, name="Apple"
        )

        ingredient2 = Ingredient.objects.create(
            user=self.user, name="Açai"
        )

        recipe = Recipe.objects.create(
            title="Apple pie",
            time_minutes=5,
            price=3.00,
            user=self.user
        )

        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredient_assigned_unique(self):
        Ingredient.objects.create(
            user=self.user,
            name="Cupuaçu"
        )

        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Bacuri"
        )

        recipe1 = Recipe.objects.create(
            title="Coriander",
            time_minutes=10,
            price=5.00,
            user=self.user,
        )

        recipe1.ingredients.add(ingredient)

        recipe2 = Recipe.objects.create(
            title="Açai com Peixe Frito",
            time_minutes=30,
            price=25.00,
            user=self.user,
        )

        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
