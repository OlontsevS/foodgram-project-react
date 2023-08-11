from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserModel(AbstractUser):
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.username}, {self.email}'
