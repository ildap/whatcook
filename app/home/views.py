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


# TODO: swagger
class FoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if ingredients := self.request.GET.getlist('ingredient'):
            queryset = queryset.search(ingredients)
            self.serializer_class = FoodRecommendationSerializer
            self.get_serializer_context()

        return queryset


class IngredientViewSet(ModelViewSet, PermissionsMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientWeightViewSet(ModelViewSet, PermissionsMixin):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer
