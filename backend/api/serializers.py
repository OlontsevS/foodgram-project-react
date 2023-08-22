from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram.models import (Cart, Favorite, Ingredient, Recipe,
                             RecipeIngredient, Tag)
from users.models import Follow

User = get_user_model()


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Follow.objects.filter(user=request.user, author=obj).exists()
        )


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")
        required_fields = ("email", "username", "first_name", "last_name",
                           "password")


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj["new_password"])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data["current_password"]):
            raise serializers.ValidationError(
                {"current_password": "Неправильный пароль."}
            )
        if (validated_data["current_password"] ==
                validated_data["new_password"]):
            raise serializers.ValidationError(
                {"new_password": "Новый пароль должен отличаться от текущего."}
            )
        instance.set_password(validated_data["new_password"])
        instance.save()
        return validated_data


class FollowSerializer(serializers.ModelSerializer):
    author = UserSerializer
    user = UserSerializer

    class Meta:
        model = Follow
        fields = ("author", "user")
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("author", "user"),
                message="Вы уже подписаны на данного пользователя",
            ),
        )

    def validate(self, data):
        author = data.get("author")
        user = data.get("user")
        if user == author:
            raise serializers.ValidationError(
                {"errors": "Нельзя подписаться на самого себя"}
            )
        return data

    def create(self, validated_data):
        author = validated_data.get("author")
        user = validated_data.get("user")
        return Follow.objects.create(user=user, author=author)


class RecipesBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = (
        serializers.SerializerMethodField(method_name="get_is_subscribed"))
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = (
        serializers.SerializerMethodField(method_name="get_recipes_count"))

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj) -> Follow:
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Follow.objects.filter(user=request.user, author=obj).exists()
        )

    def get_recipes(self, obj) -> dict:
        request = self.context.get("request")
        recipes_limit = request.POST.get("recipes_limit")
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:(recipes_limit)]
        return RecipesBriefSerializer(queryset, many=True).data

    def get_recipes_count(self, obj) -> int:
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = (
        serializers.ReadOnlyField(source="ingredient.measurement_unit"))

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source="recipes"
    )
    image = Base64ImageField()
    author = UserGetSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user

        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user

        return (
            user.is_authenticated
            and Cart.objects.filter(user=user, recipe=obj).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserGetSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
        extra_kwargs = {
            "ingredients": {"required": True, "allow_blank": False},
            "tags": {"required": True, "allow_blank": False},
            "name": {"required": True, "allow_blank": False},
            "text": {"required": True, "allow_blank": False},
            "image": {"required": True, "allow_blank": False},
            "cooking_time": {"required": True},
        }

    def validate(self, obj):
        for field in ["name", "text", "cooking_time"]:
            if not obj.get(field):
                raise serializers.ValidationError(
                    f"{field} - Обязательное поле."
                )
        if not obj.get("tags"):
            raise serializers.ValidationError("Нужно указать минимум 1 тег.")
        if not obj.get("ingredients"):
            raise serializers.ValidationError(
                "Нужно указать минимум 1 ингредиент."
            )
        inrgedient_id_list = [item["id"] for item in obj.get("ingredients")]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальны."
            )
        return obj

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(pk=ingredient["id"]),
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        RecipeIngredient.objects.filter(
            recipe=instance, ingredient__in=instance.ingredients.all()
        ).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class CartSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
