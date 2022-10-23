from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from core.models import Ingredient, Tag, Recipe, IngredientRecipe
from rest_framework.fields import SerializerMethodField
from rest_framework import status
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model


User = get_user_model()

FIELDS = (
    'email',
    'id',
    'username',
    'first_name',
    'last_name',
    'password'
)


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class UserSerializer(UserSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = FIELDS

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError("Choose another name")
        return value

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscribing.filter(author=obj).exists()


class SubscribeSerializer(UserSerializer):
    """Сериализатор для подписок"""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if user.subscribing.filter(author=author).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


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
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов"""
    author = UserSerializer(read_only=True)
    name = serializers.CharField(max_length=254)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(allow_null=True)
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time']

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError('Отсутствие ингредиентов')
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients:
                raise ValidationError(
                    f'Такой ингредиент:{ingredient} уже добавлен'
                )
            amount = ingredient['amount']
            if not int(amount) > 0:
                raise ValidationError('Недопустимое количество ингредиентов')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('Отсутствие тега')
        validated_tags = set()
        for tag in tags:
            validated_tags.add(tag)
        return validated_tags

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзатор для отображения рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_recipes'
    )
    image = Base64ImageField(allow_null=True)
    name = serializers.CharField(max_length=254)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time']


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в сокращённой форме"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
