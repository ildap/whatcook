from rest_framework.routers import DefaultRouter
from home.views import FoodViewSet, IngredientViewSet, IngredientWeightViewSet
from django.urls import include, path


router = DefaultRouter()
router.register(r'foods', FoodViewSet)
router.register(r'ingredient', IngredientViewSet)
router.register(r'ingredient_weight', IngredientWeightViewSet)

app_name = 'home'

urlpatterns = [
    path(r'', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
