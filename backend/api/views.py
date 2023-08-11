from django.contrib.auth import get_user_model
import djoser.views
from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from foodgram.models import Ingridient, Tag, Recipe, Favorite, Cart
from .serializers import FavoriteSerializer, IngridientSerializer, TagSerializer, RecipeSerializer, CartSerializer
from .paginations import CustomPagination


User = get_user_model()


class CustomUserViewSet(djoser.views.UserViewSet):
    pagination_class = CustomPagination
    queryset = User.objects.all()


class IngridientViewSet(viewsets.ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return recipe.favorites.all()


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
