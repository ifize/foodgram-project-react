from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UsersViewSet
from .views import (TagViewSet, IngredientViewSet, RecipeViewSet)

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')

urlpatterns = (
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)