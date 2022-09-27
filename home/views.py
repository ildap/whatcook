from rest_framework.viewsets import ModelViewSet
from home.models import Food, Ingredient, IngredientWeight
from home.serializers import FoodSerializer, IngredientSerializer, IngredientWeightSerializer


class FoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientWeightViewSet(ModelViewSet):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer
