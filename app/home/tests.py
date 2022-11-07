from abc import ABCMeta, abstractmethod

from django.contrib.auth.models import User
from django.db.models import QuerySet, ObjectDoesNotExist
from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from home.views import FoodViewSet, FoodRecommendationListView
from home.models import Food, Ingredient, FoodRecommendation


class ModelViewSetTestMixin:
    """
    Mixin class for testing 'crud' methods from ModelViewSet subclasses
    """
    __metaclass__ = ABCMeta

    def setUp(self):
        self.factory = APIRequestFactory()
        self.detail_view = self.get_viewset_class().as_view({'get': 'retrieve'})
        self.view = self.get_viewset_class().as_view({'get': 'list', 'post': 'create',
                                                      'put': 'update', 'delete': 'destroy'})

    @abstractmethod
    def get_queryset(self) -> QuerySet:
        pass

    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def get_viewset_class(self) -> ModelViewSet.__class__:
        pass

    @abstractmethod
    def validation_testcases(self) -> list:
        """
        Return list of test cases with no valid data and relevant error.

        return [
            {
                'no valid data': {'field name1': 'value', 'field name2': ''},
                'error codes':   {'field name2': 'blank'}
            },
        ]
        """

    @abstractmethod
    def get_valid_data(self) -> dict:
        pass

    @abstractmethod
    def is_correct_serialize(self, model_object, serialize_data) -> bool:
        pass

    def test_list(self):
        request = self.factory.get(self.get_url(), format='json')
        response = self.view(request)
        model_count = self.get_queryset().count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], model_count)

    def test_create_no_valid(self):
        for testcase in self.validation_testcases():
            data = testcase['no valid data']
            error_codes = testcase['error codes']
            request = self.factory.post(self.get_url(), data=data, format='json')
            response = self.view(request)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            for field_key in error_codes:
                first_code = response.data[field_key][0].code
                second_code = error_codes[field_key]
                self.assertEqual(first_code, second_code)

    def test_create_valid(self):
        request = self.factory.post(self.get_url(),
                                    data=self.get_valid_data(),
                                    format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:
            self.get_queryset().get(pk=response.data['pk'])
        except ObjectDoesNotExist:
            self.fail("object not created")

    def test_retrieve(self):
        obj = self.get_queryset().first()
        request = self.factory.get(self.get_url() + str(obj.pk), format='json')
        response = self.detail_view(request, pk=obj.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if not self.is_correct_serialize(obj, response.data):
            self.fail("no correct serialization")

    def test_update(self):
        obj = self.get_queryset().first()
        request = self.factory.put(self.get_url() + str(obj.pk),
                                   data=self.get_valid_data(),
                                   format='json')
        response = self.view(request, pk=obj.pk)
        updated_obj = self.get_queryset().first()
        # for comparing without pk
        updated_obj.pk = None

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(updated_obj, obj)

    def test_delete(self):
        obj = self.get_queryset().first()
        request = self.factory.delete(self.get_url() + str(obj.pk), format='json')
        response = self.view(request, pk=obj.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            self.get_queryset().get(pk=obj.pk)


class FoodViewSetTest(ModelViewSetTestMixin, TestCase):
    fixtures = ['_data.json']

    user = User.objects.get(username='GoodUser') # aOwnf2gjOwP9n
    anonymous = User.objects.get(username='AnonymousUser')

    # Implemented abstract methods
    def get_viewset_class(self) -> ModelViewSet.__class__:
        return FoodViewSet

    def get_url(self):
        return "/foods/"

    def get_queryset(self) -> QuerySet:
        return Food.objects.get_queryset()

    def validation_testcases(self):
        long_string = 'L' * 256
        blank_string = ''
        return [
            {
                'no valid data': {'name': blank_string, 'description': long_string},
                'error codes': {'name': 'blank', 'description': 'max_length'}
            }
        ]

    def get_valid_data(self) -> dict:
        return {'name': 'pizza'}

    def is_correct_serialize(self, model_object, serialize_data) -> bool:
        return model_object.pk == serialize_data.get('pk') and \
               model_object.name == serialize_data.get('name') and \
               model_object.description == serialize_data.get('description')

    # Test cases
    def test_create_unique(self):
        request = self.factory.post(self.get_url(),
                                    data={'name': 'carbonara'}, format='json')
        response = self.view(request)

        self.assertEqual(response.data['name'][0].code, 'unique')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FoodRecommendationListViewTest(TestCase):
    fixtures = ['_data.json']

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
    fixtures = ['_data.json']

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
    fixtures = ['_data.json']

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

