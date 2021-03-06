from unittest.mock import patch
from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase


def sample_user(email="teste@henrique.com", password="testpass"):
    """CREATE A SAMPLE USER"""
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """TEST THE TAG STRING REPRESENTATION"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan"
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """TEST THE INGREDIENT STRING REPRESENTATION"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """TEST THE RECIPE STRING REPRESENTATION"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Steak and mushroom sauce",
            time_minutes=5,
            price=5.00,
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """TEST THAT IMAGE IS SAVED TO THE CORRECT LOCATION"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f"uploads/recipe/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)
