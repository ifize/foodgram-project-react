from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from core.models import Ingredient, Tag, Recipe, Favorite
from .serializers import RecipeReadSerializer, IngredientSerializer, TagSerializer, AddRecipeSerializer, ShortRecipeSerializer
from .permissions import IsAdminAuthorOrReadOnlyPermission
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404
from .filters import RecipeFilter
from django_filters.rest_framework import DjangoFilterBackend


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('ingredient__name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return AddRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_recipe(Favorite, request.user, pk)

    def add_recipe(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response('Этот рецпт уже есть',
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Такого рецепта уже нет',
                        status=status.HTTP_400_BAD_REQUEST)
