from core.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                         ShoppingCart, Tag)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminAuthorOrReadOnlyPermission
from .serializers import (AddRecipeSerializer, IngredientSerializer,
                          RecipeReadSerializer, ShortRecipeSerializer,
                          TagSerializer)


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
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        return queryset.filter(name__startswith=name)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
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
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request.user, pk)
        return self.delete_recipe(ShoppingCart, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(Favorite, request.user, pk)
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

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredient_list = 'Cписок покупок:'
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount_sum=Sum('amount'))
        for num, i in enumerate(ingredients):
            ingredient_list += (
                f"\n{i['ingredient__name']} - "
                f"{i['amount_sum']} {i['ingredient__measurement_unit']}"
            )
            if num < ingredients.count() - 1:
                ingredient_list += ', '
        file = 'shopping_list'
        response = HttpResponse(
            ingredient_list, 'Content-Type: application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return response
