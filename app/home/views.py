from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView


from .permissions import DjangoObjectPermissionsOrAnonReadOnly, assign_object_perms
from .models import (
    Food,
    Ingredient,
    IngredientWeight,
    FoodRecommendation
)
from .serializers import (
    FoodSerializer,
    IngredientSerializer,
    IngredientWeightSerializer,
    FoodRecommendationSerializer
)

# TODO: swagger
class Permissions:
    permission_classes = [DjangoObjectPermissionsOrAnonReadOnly]

    def perform_create(self, serializer):
        obj = serializer.save()
        assign_object_perms(self.request.user, obj)


class FoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if ingredients := self.request.GET.getlist('ingredient'):
            queryset = queryset.search(ingredients)

        return queryset


class FoodRecommendationListView(ListAPIView):
    serializer_class = FoodRecommendationSerializer

    def get_queryset(self):
        ingredients_pk = self.kwargs['ingredients'].split(',')
        ingredients = Ingredient.objects.filter(pk__in=ingredients_pk)
        return FoodRecommendation.objects.filter_by_ingredients(ingredients)


class IngredientViewSet(ModelViewSet, Permissions):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientWeightViewSet(ModelViewSet, Permissions):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer