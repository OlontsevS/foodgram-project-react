from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('recipe/<int:recipe_id>/', views.recipe),
    path('recipe/new/', views.recipe_create),
    path('recipe/<int:recipe_id>/', views.recipe_edit),
    path('favorites/', views.favorites),
    path('profile/<str:username>/', views.profile),
    path('follow/', views.follow_index),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]