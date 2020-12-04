from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """ TEST => CRIANDO UM NOVO USUÁRIO COM EMAIL => SUCESSO"""
        email = "p13dr0h@gmail.com"
        password = "TestSenha321"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize_sucessful(self):
        """ TEST => NORMALIZAR O EMAIL DE UM NOVO USUÁRIO => SUCESSO"""
        email = "p13dr0h@gMaiL.com"
        password = "TestSenha321"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email_fail(self):
        """ TEST => CRIAR UM USUARIO COM UM EMAIL INVALIDO => FALHA"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "TeuTueEutUet")

    def test_create_superuser_sucessful(self):
        """TEST => CRIAR UM SUPER USUÁRIO"""
        user = get_user_model().objects.create_superuser(
            "p13dr0h@gmail.com",
            "testzineo"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
