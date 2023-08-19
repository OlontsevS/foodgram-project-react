from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
import djoser.views
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from foodgram.models import Ingredient, Tag, Recipe, Favorite, Cart, RecipeIngredient
from users.models import Follow
from .filters import RecipeFilter
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    CartSerializer,
    UserCreateSerializer,
    UserGetSerializer,
    FollowSerializer,
    SubscribeSerializer,
    SetPasswordSerializer,
)
from .paginations import CustomPagination


User = get_user_model()


class CustomUserViewSet(djoser.views.UserViewSet):
    pagination_class = CustomPagination
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "set_password":
            return SetPasswordSerializer
        if self.action == "create":
            return UserCreateSerializer
        return UserGetSerializer

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = FollowSerializer(data={"user": user.id, "author": author.id})
        if request.method == "POST":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = SubscribeSerializer(author, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = Follow.objects.filter(user=user, author=author)
        if not follow.exists():
            return Response(
                {"errors": "У вас нет данного пользователя в подписках"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("GET",),
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
        url_path="favorite",
        url_name="favorite",
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {
                        "errors": f'Повторно - "{recipe.name}" добавить нельзя,'
                        f"он уже есть в избранном у пользователя"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            obj = Favorite.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": f'В избранном нет рецепта "{recipe.name}"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
        url_path="shopping_cart",
        url_name="shopping_cart",
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            if Cart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {
                        "errors": f'Повторно - "{recipe.name}" добавить нельзя,'
                        f"он уже есть в списке покупок"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Cart.objects.create(user=user, recipe=recipe)
            serializer = CartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            obj = Cart.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {
                    "errors": f'Нельзя удалить рецепт - "{recipe.name}", '
                    f"которого нет в списке покупок "
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects.values("ingredient")
            .annotate(total_amount=Sum("amount"))
            .values_list(
                "ingredient__name", "total_amount", "ingredient__measurement_unit"
            )
        )

        file_list = []
        [
            file_list.append("{} - {} {}.".format(*ingredient))
            for ingredient in ingredients
        ]
        file = HttpResponse(
            "Cписок покупок:\n" + "\n".join(file_list), content_type="text/plain"
        )
        file["Content-Disposition"] = "attachment; filename=shopping_cart.txt"
        return file


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user.id
        return Favorite.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["recipe_id"] = self.kwargs.get("recipe_id")
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            favorite_recipe=get_object_or_404(Recipe, id=self.kwargs.get("recipe_id")),
        )


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user.id
        return Cart.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["recipe_id"] = self.kwargs.get("recipe_id")
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            shopping_cart=get_object_or_404(Recipe, id=self.kwargs.get("recipe_id")),
        )
