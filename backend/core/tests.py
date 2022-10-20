from django.test import TestCase

from .models import Ingredient


class IngredientModelTestCase(TestCase):

    def setUp(self) -> None:
        self.ingredient = Ingredient.objects.create()

    def test_name(self):
        self.assertEqual(str(self.ingredient), self.ingredient.name)
