# Generated by Django 2.2.16 on 2022-10-24 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20221023_1925'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_ingredient_recipe'),
        ),
    ]
