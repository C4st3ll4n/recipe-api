import tempfile
import os
from PIL import Image
from core.models import Recipe, Tag, Ingredient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPE_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id):
    """RETURN URL FOR RECIPE IMAGE"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


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

    def test_add_basic_recipe_success(self):
        """TEST CREATING RECIPE"""""

        recipe_payload = {
            'title': "Cheesecake",
            'time_minutes': 30,
            'price': 5.00
        }

        res = self.client.post(RECIPE_URL, recipe_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for k in recipe_payload.keys():
            self.assertEqual(recipe_payload[k], getattr(recipe, k))

    def test_add_recipe_with_tag_success(self):
        tag1 = sample_tag(self.user, name="Cake")
        tag2 = sample_tag(self.user, name="Vegan")

        recipe_payload = {
            'title': "Avocado cake",
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 5.00
        }

        res = self.client.post(RECIPE_URL, recipe_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 2)

        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_add_recipe_with_ingredient_success(self):
        tag = sample_tag(self.user, name="Vegan")

        ingredient1 = sample_ingredient(self.user, name="Ginger")
        ingredient2 = sample_ingredient(self.user, name="Prawns")

        recipe_payload = {
            'title': "Thai prwan red curry",
            'ingredients': [ingredient1.id, ingredient2.id],
            'tags': [tag.id],
            'time_minutes': 20,
            'price': 5.00
        }

        res = self.client.post(RECIPE_URL, recipe_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 2)

        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """TEST UPDATE A RECIPE WITH PATCH"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(self.user))

        new_tag = sample_tag(self.user, name='Curry')

        recipe_payload = {
            "title": "Chiken tikka",
            'tags': [new_tag.id]
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, recipe_payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, recipe_payload['title'])
        self.assertEqual(recipe.tags.count(), 1)

        tags = Tag.objects.all()
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """TEST UPDATE RECIPE WITH PUT"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(self.user))

        recipe_payload = {
            "title": "Spaghetti carbonara",
            'time_minutes': 25,
            'price': 5.0,
            'tags': []
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, recipe_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, recipe_payload['title'])
        self.assertEqual(recipe.time_minutes, recipe_payload['time_minutes'])
        self.assertEqual(recipe.price, recipe_payload['price'])
        self.assertEqual(recipe.tags.count(), 0)

        tags = Tag.objects.all()
        self.assertEqual(len(tags), 1)

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


class RecipeImageUploadTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "p13dr0h@teste.com",
            "p1p31p31p3p13p1p31"
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(self.user)

    def tearDown(self) -> None:
        """REMOVE TEMP FILES"""
        self.recipe.img.delete()

    def test_upload_recipe_img(self):
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)

            res = self.client.post(url, {'img': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        #   print(f"\n{res.data}\n")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('img', res.data)
        self.assertTrue(os.path.exists(self.recipe.img.path))

    def test_img_upload_fail(self):
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'img': 'not a img'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
