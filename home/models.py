from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)
    calories = models.FloatField()

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class IngredientWeight(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    weight = models.FloatField()

