from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

from .views import (
    FoodViewSet,
    IngredientViewSet,
    IngredientWeightViewSet,
)

router = DefaultRouter()
router.register(r'foods', FoodViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'ingredient_weights', IngredientWeightViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
]
