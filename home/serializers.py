from rest_framework import serializers
from home.models import Food, Ingredient, IngredientWeight, FoodRecommendation


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        depth = 2
        fields = ['pk', 'name', 'description', 'ingredientweight_set']


class FoodRecommendationSerializer(serializers.ModelSerializer):
    has_ingredients = serializers.SerializerMethodField()
    absent_ingredients = serializers.SerializerMethodField()

    def get_has_ingredients(self, food_recommendation):
        return IngredientSerializer(food_recommendation.has_ingredients, many=True).data

    def get_absent_ingredients(self, food_recommendation):
        return IngredientSerializer(food_recommendation.absent_ingredients, many=True).data

    class Meta:
        model = FoodRecommendation
        fields = ['pk', 'name', 'description', 'has_ingredients', 'absent_ingredients']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['pk', 'name', 'calories']


class IngredientWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientWeight
        fields = ['pk', 'food', 'ingredient', 'weight']
