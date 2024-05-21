from django.db.models.signals import post_save
from django.dispatch import receiver
from home.models import IngredientWeight


@receiver(post_save, sender=IngredientWeight)
def on_ingredient_weight_save(sender, instance, **kwargs):
    instance.food._update_vector()
    instance.food.save()
