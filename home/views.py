from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from home.permissions import DjangoObjectPermissionsOrAnonReadOnly, assign_object_perms
from home.models import (
    Food,
    Ingredient,
    IngredientWeight,
    FoodRecommendation
)
from home.serializers import (
    FoodSerializer,
    IngredientSerializer,
    IngredientWeightSerializer,
    FoodRecommendationSerializer
)


class ModelViewSetAndPerms(ModelViewSet):
    permission_classes = [DjangoObjectPermissionsOrAnonReadOnly]

    def perform_create(self, serializer):
        obj = serializer.save()
        assign_object_perms(self.request.user, obj)


class FoodViewSet(ModelViewSetAndPerms):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer


class FoodRecommendationListView(ListAPIView):
    serializer_class = FoodRecommendationSerializer

    def get_queryset(self):
        ingredients_pk = self.kwargs['ingredients'].split(',')
        ingredients = Ingredient.objects.filter(pk__in=ingredients_pk)
        return FoodRecommendation.objects.filter_by_ingredients(ingredients)


class IngredientViewSet(ModelViewSetAndPerms):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientWeightViewSet(ModelViewSetAndPerms):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer