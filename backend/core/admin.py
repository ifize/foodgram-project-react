from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Ingredient, IngredientRecipe, Recipe, Tag


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 2


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'get_image',
    )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
        ('image',),
    )
    raw_id_fields = ('author', )
    search_fields = (
        'name', 'author',
    )
    list_filter = (
        'name', 'author__username',
    )

    inlines = (IngredientInline,)
    save_on_top = True

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" hieght="100"')

    get_image.short_description = 'Изображение'


admin.site.register(Tag)
admin.site.register(Ingredient)
