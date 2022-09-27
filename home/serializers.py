from rest_framework import serializers
from home.models import Food, Ingredient, IngredientWeight


class FoodSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="home:food-detail", lookup_field='pk')
    """
    TODO relation field ingredients: IngredientWeight[]
    """
    class Meta:
        model = Food
        fields = ["name", "description", "url"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["name", "calories"]


class IngredientWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientWeight
        fields = ["food", "ingredient", "weight"]
