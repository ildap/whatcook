from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from home.models import Food, Ingredient, IngredientWeight, FoodRecommendation
from home.serializers import (FoodSerializer, IngredientSerializer,
                              IngredientWeightSerializer, FoodRecommendationSerializer)


class FoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer


class FoodRecommendationListView(ListAPIView):
    serializer_class = FoodRecommendationSerializer

    def get_queryset(self):
        ingredients_pk = self.kwargs['ingredients'].split(',')
        ingredients = Ingredient.objects.filter(pk__in=ingredients_pk)
        return FoodRecommendation.objects.filter_by_ingredients(ingredients)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientWeightViewSet(ModelViewSet):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer
