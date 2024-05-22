from rest_framework import serializers

from .models import (
    Food,
    Ingredient,
    IngredientWeight,
)


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        depth = 1
        fields = ['pk', 'name', 'description', 'ingredients']


class FoodRecommendationSerializer(FoodSerializer):
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, food):
        ingredients = self.context['request'].GET.getlist('ingredient')
        data = IngredientSerializer(food.ingredients, many=True).data
        for i in data:
            if i['name'] in ingredients:
                i['absent'] = False
            else:
                i['absent'] =True

        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['pk', 'name', 'calories']


class IngredientWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientWeight
        fields = ['pk', 'food', 'ingredient', 'weight']
