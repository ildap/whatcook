from django.contrib.auth.models import User
from django.db.models import QuerySet, ObjectDoesNotExist
from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from .views import FoodViewSet, FoodRecommendationListView, IngredientViewSet, IngredientWeightViewSet
from .models import Food, Ingredient, FoodRecommendation, IngredientWeight


class ModelViewSetTestMixin:
    """Mixin class for testing 'crud' methods from ModelViewSet subclasses"""
    view_set_class: ModelViewSet.__class__
    queryset: QuerySet
    user: User
    url = ""

    # Contain list of test cases with no valid data and relevant error.
    # [
    #    {
    #        'no valid data': {'field name1': 'value', 'field name2': ''},
    #        'error codes':   {'field name2': 'blank'}
    #    },
    # ]
    validation_testcases = []
    valid_data = {}

    def setUp(self):
        self.factory = APIRequestFactory()
        self.detail_view = self.view_set_class.as_view({'get': 'retrieve'})
        self.view = self.view_set_class.as_view({'get': 'list', 'post': 'create',
                                                 'put': 'update', 'delete': 'destroy'})

    def test_list(self):
        request = self.factory.get(self.url, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        model_count = self.queryset.count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], model_count)

    def test_create_no_valid(self):
        for testcase in self.validation_testcases:
            data = testcase['no valid data']
            error_codes = testcase['error codes']

            request = self.factory.post(self.url, data=data, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            for field_key in error_codes:
                first_code = response.data[field_key][0].code
                second_code = error_codes[field_key]
                self.assertEqual(first_code, second_code)

    def test_create_valid(self):
        request = self.factory.post(self.url,
                                    data=self.valid_data,
                                    format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:
            self.queryset.get(pk=response.data['pk'])
        except ObjectDoesNotExist:
            self.fail("object not created")

    def test_retrieve(self):
        obj = self.queryset.first()
        request = self.factory.get(self.url + str(obj.pk), format='json')
        force_authenticate(request, user=self.user)
        response = self.detail_view(request, pk=obj.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if not self.is_correct_serialize(obj, response.data):
            self.fail("no correct serialization")

    def test_update(self):
        obj = self.queryset.first()
        request = self.factory.put(self.url + str(obj.pk),
                                   data=self.valid_data,
                                   format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=obj.pk)
        updated_obj = self.queryset.first()

        # for comparing without pk
        updated_obj.pk = None

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(updated_obj, obj)

    def test_delete(self):
        obj = self.queryset.first()
        request = self.factory.delete(self.url + str(obj.pk), format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request, pk=obj.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            self.queryset.get(pk=obj.pk)


class FoodViewSetTest(ModelViewSetTestMixin, TestCase):
    fixtures = ['data.json']
    view_set_class = FoodViewSet
    queryset = Food.objects.get_queryset()
    user = User.objects.get(username='GoodUser')
    url = "/foods/"

    _long_string = 'L' * 256
    _blank_string = ''
    validation_testcases = [
        {
            'no valid data': {},
            'error codes': {'name': 'required'}
        },
        {
            'no valid data': {'name': _blank_string, 'description': _long_string},
            'error codes': {'name': 'blank', 'description': 'max_length'}
        }
    ]
    valid_data = {'name': 'pizza'}

    def is_correct_serialize(self, model_object, serialize_data) -> bool:
        return model_object.pk == serialize_data.get('pk') and \
               model_object.name == serialize_data.get('name') and \
               model_object.description == serialize_data.get('description')

    def test_create_unique(self):
        request = self.factory.post(self.url,
                                    data={'name': 'carbonara'}, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.data['name'][0].code, 'unique')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IngredientViewSetTest(ModelViewSetTestMixin, TestCase):
    fixtures = ['data.json']
    view_set_class = IngredientViewSet
    queryset = Ingredient.objects.get_queryset()
    user = User.objects.get(username='GoodUser')
    url = "/ingredients/"

    _long_string = 'L' * 256
    _blank_string = ''
    validation_testcases = [
        {
            'no valid data': {},
            'error codes': {'name': 'required'}
        },
        {
            'no valid data': {'name': _blank_string},
            'error codes': {'name': 'blank'}
        },
        {
            'no valid data': {'name': _long_string},
            'error codes': {'name': 'max_length'}
        }
    ]
    valid_data = {'name': "mango", 'calories': 1}

    def is_correct_serialize(self, model_object, serialize_data) -> bool:
        return model_object.pk == serialize_data.get('pk') and \
               model_object.name == serialize_data.get('name') and \
               model_object.calories == serialize_data.get('calories')


class IngredientWeightViewSetTest(ModelViewSetTestMixin, TestCase):
    fixtures = ['data.json']
    view_set_class = IngredientWeightViewSet
    queryset = IngredientWeight.objects.get_queryset()
    user = User.objects.get(username='GoodUser')
    url = "/ingredient_weights/"

    validation_testcases = [
        {
            'no valid data': {},
            'error codes': {'food': 'required', 'ingredient': 'required', 'weight': 'required'}
        },
        {
            'no valid data': {'food': 99, 'ingredient': 99, 'weight': 'invalid'},
            'error codes': {'food': 'does_not_exist', 'ingredient': 'does_not_exist', 'weight': 'invalid'}
        },

    ]
    valid_data = {'food': 4, 'ingredient': 5, 'weight': 10}

    def is_correct_serialize(self, model_object, serialize_data) -> bool:
        return model_object.pk == serialize_data.get('pk') and \
               model_object.food_id == serialize_data.get('food') and \
               model_object.weight == serialize_data.get('weight') and \
               model_object.ingredient_id == serialize_data.get('ingredient')


class FoodRecommendationListViewTest(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = FoodRecommendationListView.as_view()
        self.url = "/foods/recommendation"

    def test_list(self):
        ingredients = Ingredient.objects.filter(name__in=['pasta', 'eggs'])
        ingredients_pk = ','.join([str(i.pk) for i in Ingredient.objects.filter(name__in=['pasta', 'eggs'])])
        request = self.factory.get(self.url + '/' + ingredients_pk, format='json')
        response = self.view(request, ingredients=ingredients_pk)
        model_count = FoodRecommendation.objects.filter_by_ingredients(ingredients).count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], model_count)

        request = self.client.get(self.url + "/no valid", format='json')
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)


class FoodRecommendationManagerTest(TestCase):
    fixtures = ['data.json']

    def assertContainIngredients(self, available_ingredients, need_ingredients):
        contain_ingredient = False
        for ingredient in need_ingredients:
            if ingredient in available_ingredients:
                contain_ingredient = True
                break

        self.assertTrue(contain_ingredient, msg="FoodRecommendation doesn't have the required ingredients")

    def test_filter_by_ingredients(self):
        ingredients = Ingredient.objects.filter(name__in=['pasta', 'eggs'])
        food_recommendations = FoodRecommendation.objects.filter_by_ingredients(ingredients)
        max_count = ingredients.count()
        prev_count = max_count

        for food_recommendation in food_recommendations:
            available_ingredients = [iw.ingredient for iw in food_recommendation.ingredientweight_set.all()]

            self.assertContainIngredients(available_ingredients, ingredients)
            # test order by ingredients_count
            self.assertLessEqual(food_recommendation.ingredients_count, prev_count)

            if food_recommendation.ingredients_total > food_recommendation.ingredients_count:
                self.assertIsNotNone(food_recommendation.absent)

            prev_count = food_recommendation.ingredients_count

    def test_filter_by_ingredients_no_ingredients(self):
        food_recommendations = FoodRecommendation.objects.filter_by_ingredients([])

        self.assertEqual(food_recommendations.count(), 0)


class FoodRecommendationTest(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.food_recommendation = FoodRecommendation.objects.get(name='omelet')
        self.absent_pk = self.food_recommendation.ingredientweight_set.all()[0].ingredient.pk
        self.food_recommendation.absent = str(self.absent_pk)

    def test_has_ingredients(self):
        has_ingredients = self.food_recommendation.has_ingredients
        ingredients = [iw.ingredient for iw in self.food_recommendation.ingredientweight_set.all()[0:]]

        self.assertEqual(set(has_ingredients), set(ingredients))

    def test_absent_ingredients(self):
        absent_ingredients = self.food_recommendation.absent_ingredients

        self.assertEqual(len(absent_ingredients), 1)
        self.assertEqual(absent_ingredients[0].pk, self.absent_pk)
