from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (CartViewSet, CustomUserViewSet, FavoriteViewSet,
                    IngredientViewSet, RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register("users", CustomUserViewSet, basename="users")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("tags", TagViewSet, basename="tags")
router.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    FavoriteViewSet,
    basename="favorite"
)
router.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    CartViewSet,
    basename="shoppingcart"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path('api-token-auth/', views.obtain_auth_token),
]
