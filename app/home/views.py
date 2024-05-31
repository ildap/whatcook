from rest_framework.viewsets import ModelViewSet

from .permissions import PermissionsMixin
from .models import (
    Food,
    Ingredient,
    IngredientWeight
)
from .serializers import (
    FoodSerializer,
    IngredientSerializer,
    IngredientWeightSerializer,
    FoodRecommendationSerializer
)


class FoodViewSet(PermissionsMixin, ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if ingredients := self.request.GET.getlist('ingredient'):
            queryset = queryset.search(ingredients)
            self.serializer_class = FoodRecommendationSerializer

        return queryset


class IngredientViewSet(PermissionsMixin, ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientWeightViewSet(PermissionsMixin, ModelViewSet):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer
