from django.db import models, connection
from django.db.models import Q, Count, F
from django.db.models.expressions import Value


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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class IngredientWeight(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    weight = models.FloatField()

    class Meta:
        ordering = ['-id']


class FoodRecommendationManager(models.Manager):

    def filter_by_ingredients(self, ingredients: [Ingredient]):
        ingredient_in = Q(ingredientweight__ingredient__in=ingredients)
        absent_ids = models.Aggregate(F('ingredientweight__ingredient_id'),
                                      function='GROUP_CONCAT', filter=~ingredient_in)

        if connection.vendor == 'postgresql':
            absent_array = models.Aggregate(F('ingredientweight__ingredient_id'),
                                            function='array_agg', filter=~ingredient_in)
            absent_ids = models.Func(absent_array, Value(','), function='array_to_string',
                                     output_field=models.TextField())

        return (self.get_queryset()
                .annotate(ingredients_count=Count('ingredientweight', filter=ingredient_in),
                          ingredients_total=Count('ingredientweight'),
                          absent=absent_ids)
                .filter(ingredients_count__gt=0)
                .order_by('-ingredients_count', 'ingredients_total'))


class FoodRecommendation(Food):
    objects = FoodRecommendationManager()

    class Meta:
        proxy = True

    @property
    def has_ingredients(self):
        return [iw.ingredient for iw in self.ingredientweight_set.exclude(pk__in=self._absent_ids())]

    @property
    def absent_ingredients(self):
        return Ingredient.objects.filter(pk__in=self._absent_ids()).all()

    def _absent_ids(self):
        if hasattr(self, 'absent') and isinstance(self.absent, str):
            return self.absent.split(',')

        return []
