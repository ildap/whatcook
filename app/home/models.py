from django.db import models
from django.db.models.expressions import Value

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector

from home import managers


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)
    calories = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class Food(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField(Ingredient, through="IngredientWeight")
    _ingredients_vector = SearchVectorField()

    objects = managers.FoodManager()

    def __str__(self):
        return self.name

    def _update_vector(self):
        ingredients_str = " ".join(self.ingredients.values_list("name", flat=True))
        self._ingredients_vector = SearchVector(Value(f"'{ingredients_str}'"))

    class Meta:
        ordering = ['-id']
        indexes = [
            GinIndex(fields=["_ingredients_vector"]),
        ]


class IngredientWeight(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    weight = models.FloatField(default=0)

    class Meta:
        ordering = ['-id']
