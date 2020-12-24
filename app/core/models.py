import uuid
import os

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, \
    BaseUserManager, PermissionsMixin
from django.db import models


def recipe_image_file_path(instance, file_name):
    """GENERATE THE FILE PATH FOR THE NEW IMAGE """
    ext = file_name.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """CRIA E SALVA UM, NOVO USUÁRIO"""
        if not email:
            raise ValueError("Usuário deve ter um email válido !")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """CRIA E SALVA UM, NOVO SUPER USUÁRIO"""
        if not email:
            raise ValueError("Usuário deve ter um email válido !")

        if not password:
            raise ValueError("Usuário deve ter uma senha válida !")

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """CLASSE DE USUÁRIO CUSTOMIZADA, QUE SUPORTA
     EMAIL EM DETRIMENTO DE USUARIO"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    time_minutes = models.IntegerField()
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    img = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
