from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UsersViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')

urlpatterns = (
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)
# v1_auth_patterns = [
#     path('signup/', sign_up, name='sign_up'),
#     path('token/', retrieve_token, name='retrieve_token'),
# ]

# urlpatterns = [
#     path('', include(router_v1.urls)),
#     path('auth/', include(v1_auth_patterns)),
# ]
