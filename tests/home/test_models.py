from django.db.models import Value
from django.test import TestCase
from django.contrib.postgres.search import SearchVector

from home.models import Food, IngredientWeight, Ingredient


class FoodTestCase(TestCase):

    def setUp(self):
        self.food = Food.objects.create(name='test_food')
        self.food.ingredients.add(Ingredient.objects.create(name='test_ingredient1', calories=100))
        self.food.ingredients.add(Ingredient.objects.create(name='test_ingredient2', calories=100))
        self.food.ingredients.add(Ingredient.objects.create(name='test_ingredient3', calories=100))

    def test_update_vector(self):
        self.food._update_vector()
        vector = self.food._ingredients_vector

        self.assertIsInstance(vector, SearchVector)
        self.assertIsInstance(vector.source_expressions[0], Value)
        self.assertEqual(vector.source_expressions[0].value,
                         "'test_ingredient3 test_ingredient2 test_ingredient1'")
