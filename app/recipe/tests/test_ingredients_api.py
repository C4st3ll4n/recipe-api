from core.models import Ingredient
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
        """TEST THAT ONLY INGREDIENTS FOR THE AUTHENTICATED USER ARE RETURNED"""

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
