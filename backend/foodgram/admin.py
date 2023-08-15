from django.contrib import admin
from .models import Recipe, Tag, Ingridient, Favorite

admin.site.register(Tag)
admin.site.register(Ingridient)
admin.site.register(Recipe)
admin.site.register(Favorite)