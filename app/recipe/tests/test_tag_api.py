from core.models import Tag
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
