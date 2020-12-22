from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
ME_URL = reverse("user:me")


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

    def test_retrieve_user_unauthorized(self):
        """TEST IF THE AUTH IS REQUIRED"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """TEST API ENDPOINTS THAT NEED AUTH"""

    def setUp(self) -> None:
        self.user = create_user(email='teste@henrique.com', password='testpass', name="Pedro Testes")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_sucess(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, {
            "name": self.user.name,
            "email": self.user.email
        })

    def test_post_me_not_allowed(self):
        res = self.client.get(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ TEST UPDATE FOR AUTHENTICATED USER"""
        payload = {"name": "Lucifer", 'password': "12346987"}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

