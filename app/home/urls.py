from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

from .views import (
    FoodViewSet,
    IngredientViewSet,
    IngredientWeightViewSet,
    FoodRecommendationListView
)

router = DefaultRouter()
router.register(r'foods', FoodViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'ingredient_weights', IngredientWeightViewSet)

app_name = 'home'

urlpatterns = [
    path(r'', include(router.urls)),
    re_path('^recommendation/(?P<ingredients>[\d,]+)/$', FoodRecommendationListView.as_view()),
]
