from rest_framework import serializers

from .models import (
    Food,
    Ingredient,
    IngredientWeight,
)


class FoodSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Food
        depth = 1
        fields = ['id', 'name', 'description', 'ingredients', 'url']


class FoodRecommendationSerializer(FoodSerializer):
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, food):
        ingredients = self.context['request'].GET.getlist('ingredient')
        data = IngredientSerializer(food.ingredients, many=True).data
        for i in data:
            if i['name'] in ingredients:
                i['absent'] = False
            else:
                i['absent'] = True

        return data


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'calories', 'url']


class IngredientWeightSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IngredientWeight
        fields = ['id', 'food', 'ingredient', 'weight', 'url']
