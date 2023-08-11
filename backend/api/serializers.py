from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer

from foodgram.models import Ingridient, Tag, Recipe, Favorite

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        required_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingridient = IngridientSerializer(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('author', 'name', 'image', 'description', 'ingridients', 'tags', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    # user = CustomUserSerializer
    recipe = RecipeSerializer

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class CartSerializer(serializers.ModelSerializer):
    # user = CustomUserSerializer
    recipe = RecipeSerializer

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')