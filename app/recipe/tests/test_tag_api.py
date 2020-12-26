from core.models import Tag, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAG_URL = reverse("recipe:tag-list")


class PublicTagAPITests(TestCase):
    """TEST THE PUBLICY AVAILABLE TAG API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """TEST THAT LOGIN IS REQUIRED FOR RETRIEVING TAGS"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(TestCase):
    """TEST THE AUTHORIZED USER TAG API"""

    def setUp(self) -> None:
        self.user = get_user_model().\
            objects.create_user("test@henrique.com", "password4test")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """TEST RETRIEVING TAGS"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """TEST THAT TAGS RETURNED ARE FOR THE AUTHENTICATED USER"""
        user2 = get_user_model().\
            objects.create_user("teste@gmail.com", "senhatoTest")

        Tag.objects.create(user=user2, name="Fruity")
        main_user_tag = Tag.objects.create(user=self.user, name="Comfort food")

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], main_user_tag.name)
        # self.assertEqual(res.data[1]['name'], twoTag.name)

    def test_create_tag_sucessful(self):
        """TEST CREATING A NEW TAG"""
        tag_payload = {"name": 'Tag Test'}
        res = self.client.post(TAG_URL, tag_payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Tag.objects.filter(
            user=self.user,
            name=tag_payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """TEST CREATING A INVALID TAG -> FAIL"""
        tag_payload = {"name": ''}
        res = self.client.post(TAG_URL, tag_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tag_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Launch")

        recipe = Recipe.objects.create(
            title="Coriander",
            time_minutes=10,
            price=5.00,
            user=self.user,
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        Tag.objects.create(user=self.user, name="Breakfast")
        tag = Tag.objects.create(user=self.user, name="Launch")

        recipe1 = Recipe.objects.create(
            title="Coriander",
            time_minutes=10,
            price=5.00,
            user=self.user,
        )

        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
            title="Açai com Peixe Frito",
            time_minutes=30,
            price=25.00,
            user=self.user,
        )

        recipe2.tags.add(tag)

        res = self.client.get(TAG_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
