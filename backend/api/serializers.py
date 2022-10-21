from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from core.models import Ingredient, Tag, Recipe, IngredientRecipe
from users.serializers import UserSerializer


class Base64ImageField(serializers.ImageField):
    """Сериализатор для конвертации изображения"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов"""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связывания ингредиента с рецептом"""
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзатор для рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_recipes'
    )
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time']
