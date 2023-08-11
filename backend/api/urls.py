from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RecipeViewSet, IngridientViewSet, TagViewSet, FavoriteViewSet, CartViewSet


router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngridientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
    basename='favorite')
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', CartViewSet,
    basename='shoppingcart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
