from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.tests.test_user_api import create_user

TOKEN_URL = reverse("user:token")


class PublicUserTokenAPITests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def create_token_for_user(self):
        """TEST THAT A TOKEN IS CREATED FOR USER"""
        payload = {
            "email": "teste@gmail.com",
            'password': "aijadjiijda",
            "name": "test",
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credencials(self):
        """TEST THAT A TOKEN ISNT CREATED IF INVALID CREDENTIALS ARE GIVEN"""
        _payload = {
            "email": "teste@gmail.com",
            'password': "aijadjiijda",
            "name": "test",
        }
        create_user(**_payload)

        payload = {
            "email": "teste@gmail.com",
            'password': "wrongwrong",
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """TEST THAT TOKEN IS NOT CREATED IF USER DOESNT EXIST"""
        payload = {
            "email": "teste@gmail.com",
            'password': "wrongwrong",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        res = self.client.post(TOKEN_URL, {"email":"one", 'password':''})
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
