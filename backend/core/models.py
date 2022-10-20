from django.db import models
from users.models import User
from django.core.validators import MinValueValidator


class Tag(models.Model):
    """Класс тегов"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Тег'
    )
    color = models.CharField(
        max_length=6,
        verbose_name='Цветовой код'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:79]


class Ingredient(models.Model):
    """Класс ингредиентов"""
    name = models.CharField(
        max_length=128,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=16,
        verbose_name='Еденица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:79]


class Recipe(models.Model):
    """Класс рецептов"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    image = models.ImageField(
        upload_to='images/',
        null=False,
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField(
        null=False,
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_recipe')
        ]

    def __str__(self):
        return f'{self.name}, {self.author}'


class IngredientRecipe(models.Model):
    """Модель для реализации отношения ManyToMany ingredient_id -- recipe_id"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
    )

    class Meta:
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'
