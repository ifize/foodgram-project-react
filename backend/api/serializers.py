from core.models import Ingredient, IngredientRecipe, Recipe, Tag
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from .fields import Base64ImageField

User = get_user_model()

FIELDS = (
    'email',
    'id',
    'username',
    'first_name',
    'last_name',
    'is_subscribed'
)


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class UserSerializer(UserSerializer):
    """Сериализатор для пользователя"""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = FIELDS

    def validate_username(self, value):
        if value.lower() == 'me':
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
                detail='Вы уже подписаны на этого пользователя',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя',
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
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients]
        )

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(recipe,
                                    context=context).data


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
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        ]

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


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
