from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """TEST THE USER API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """TEST THE USER ADD SUCCESS"""
        payload = {
            "email": "test@gmail.com",
            "name": "Test",
            'password': 'test123'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_create_user_exists(self):
        """TEST CREATING A USER THAT ALREADY EXISTS"""
        payload = {
            "email": "test@gmail.com",
            "name": "Test",
            'password': 'test123'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """TEST A SHOT PASSWORD"""

        payload = {
            "email": "test@gmail.com",
            "name": "Test",
            'password': 'tTTt'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exitst = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exitst)

