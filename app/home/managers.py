from django.db import models


class FoodQuerySet(models.QuerySet):
    def search(self, ingredients):
        return self.filter(_ingredients_vector=" ".join(ingredients))


class FoodManager(models.Manager):
    def get_queryset(self):
        return FoodQuerySet(self.model, using=self._db)