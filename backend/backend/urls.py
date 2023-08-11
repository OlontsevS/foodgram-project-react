from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('api.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('auth/', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.jwt')),
]
