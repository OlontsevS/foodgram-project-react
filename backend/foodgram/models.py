from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingridient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Название ингридиента')
    measurement_unit = models.CharField(max_length=200)


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField('Label')
    description = models.TextField()
    ingridients = models.ManyToManyField(Ingridient)
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField()


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Cart(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
