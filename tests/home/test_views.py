from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from tests.home.utils import ModelViewSetTestCase

from home.views import IngredientViewSet, IngredientWeightViewSet, FoodViewSet
from home.models import Ingredient, IngredientWeight, Food

from rest_framework import status


class IngredientViewSetTestCase(ModelViewSetTestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.view = IngredientViewSet.as_view({'get': 'list', 'post': 'create',
                                               'put': 'update', 'delete': 'destroy'})
        self.retrieve_view = IngredientViewSet.as_view({'get': 'retrieve'})

    @classmethod
    def setUpTestData(cls):
        cls.auth_user = User.objects.get(username='what_cook')
        cls.obj = Ingredient.objects.first()
        cls.queryset = Ingredient.objects.get_queryset()

    def test_list(self):
        response = self.get_list("/ingredients")

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertCorrectSerialize(response.data['results'],
                                    self.queryset,
                                    self.is_correct_serialize)

    def test_retrieve(self):
        response = self.get(f"/ingredient/{self.obj.pk}", self.obj.pk)

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertTrue(self.is_correct_serialize(self.obj, response.data))

    @staticmethod
    def is_correct_serialize(model_object, serialize_data) -> bool:
        return model_object.pk == serialize_data.get('id') and \
            model_object.name == serialize_data.get('name') and \
            model_object.calories == serialize_data.get('calories')

    def test_create(self):
        response = self.post("/ingredients", {'name': 'water', 'calories': 0})

        self.assertResponseIsJson(response, status.HTTP_201_CREATED)
        try:
            obj = self.queryset.get(pk=response.data['id'])
            self.assertTrue(self.is_correct_serialize(obj, response.data))
        except ObjectDoesNotExist:
            self.fail("object not created")

    def test_create_data_required(self):
        response = self.post("/ingredients", {})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_REQUIRED,
                                                    'calories': self.CODE_REQUIRED})

    def test_create_name_blank(self):
        response = self.post("/ingredients", {'name': self.STR_BLANK})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_BLANK})

    def test_create_name_long(self):
        response = self.post("/ingredients", {'name': self.STR_LONG})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_MAX_LEN})

    def test_create_name_unique(self):
        response = self.post("/ingredients", {'name': "chicken"})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_UNIQUIE})

    def test_create_calories_invalid(self):
        response = self.post("/ingredients", {'calories': "not float"})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'calories': self.CODE_INVALID})

    def test_update(self):
        response = self.put(f"/ingredients/{self.obj.pk}", self.obj.pk, {'name': "potato",
                                                                         'calories': 80})
        updated_obj = self.queryset.get(pk=self.obj.pk)
        # compare without pk
        updated_obj.pk = None

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertNotEqual(updated_obj, self.obj)

    def test_delete(self):
        response = self.delete(f"/ingredients/{self.obj.pk}", self.obj.pk)

        self.assertResponseNoContent(response)
        with self.assertRaises(ObjectDoesNotExist):
            self.queryset.get(pk=self.obj.pk)


class IngredientWeightViewSetTestCase(ModelViewSetTestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.view = IngredientWeightViewSet.as_view({'get': 'list', 'post': 'create',
                                                     'put': 'update', 'delete': 'destroy'})
        self.retrieve_view = IngredientWeightViewSet.as_view({'get': 'retrieve'})

    @classmethod
    def setUpTestData(cls):
        cls.auth_user = User.objects.get(username='what_cook')
        cls.obj = IngredientWeight.objects.first()
        cls.queryset = IngredientWeight.objects.get_queryset()
        cls.ingredient = Ingredient.objects.first()
        cls.food = Food.objects.first()

    def test_list(self):
        response = self.get_list("/ingredients")

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertCorrectSerialize(response.data['results'],
                                    self.queryset,
                                    self.is_correct_serialize)

    def test_retrieve(self):
        response = self.get(f"/ingredient_weights/{self.obj.pk}", self.obj.pk)

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertTrue(self.is_correct_serialize(self.obj, response.data))

    def is_correct_serialize(self, model_object, serialize_data) -> bool:
        food_url = f"/foods/{model_object.food_id}/"
        ingredient_url = f"/ingredients/{model_object.ingredient_id}/"
        return model_object.pk == serialize_data.get('id') and \
            serialize_data.get('food').endswith(food_url) and \
            model_object.weight == serialize_data.get('weight') and \
            serialize_data.get('ingredient').endswith(ingredient_url)

    def test_create(self):
        food_url = f"http://testserver/foods/{self.food.id}/"
        ingredient_url = f"https://testserver/ingredients/{self.ingredient.id}/"
        response = self.post("/ingredient_weights", {'food': food_url,
                                                     'weight': 100,
                                                     'ingredient': ingredient_url})

        self.assertResponseIsJson(response, status.HTTP_201_CREATED)
        try:
            obj = self.queryset.get(pk=response.data['id'])
            self.assertTrue(self.is_correct_serialize(obj, response.data))
        except ObjectDoesNotExist:
            self.fail("object not created")

    def test_create_data_required(self):
        response = self.post("/ingredient_weights", {})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'food': self.CODE_REQUIRED,
                                                    'ingredient': self.CODE_REQUIRED})

    def test_create_weight_invalid(self):
        response = self.post("/ingredient_weights", {'weight': 'invalid'})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'weight': self.CODE_INVALID})

    def test_create_invalid_links(self):
        absent_url = f"http://testserver/foods/0/"
        invalid_url = f"/invalid_link/ingredients/1/"
        response = self.post("/ingredient_weights", {'food': absent_url,
                                                     'weight': 100,
                                                     'ingredient': invalid_url})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'food': self.CODE_DOES_NOT_EXIST,
                                                    'ingredient': self.CODE_NO_URL_MATCH})

    def test_update(self):
        food_url = f"http://testserver/foods/{self.food.id}/"
        ingredient_url = f"https://testserver/ingredients/{self.ingredient.id}/"
        response = self.put(f"/ingredient_weights/{self.obj.pk}", self.obj.pk,
                            {'food': food_url, 'weight': 10000000, 'ingredient': ingredient_url})
        updated_obj = self.queryset.get(pk=self.obj.pk)
        # compare without pk
        updated_obj.pk = None

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertNotEqual(updated_obj, self.obj)

    def test_delete(self):
        response = self.delete(f"/ingredient_weights/{self.obj.pk}", self.obj.pk)

        self.assertResponseNoContent(response)
        with self.assertRaises(ObjectDoesNotExist):
            self.queryset.get(pk=self.obj.pk)


class FoodViewSetTestCase(ModelViewSetTestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.view = FoodViewSet.as_view({'get': 'list', 'post': 'create',
                                         'put': 'update', 'delete': 'destroy'})
        self.retrieve_view = FoodViewSet.as_view({'get': 'retrieve'})

    @classmethod
    def setUpTestData(cls):
        cls.auth_user = User.objects.get(username='what_cook')
        cls.obj = Food.objects.first()
        cls.queryset = Food.objects.get_queryset()

    def test_retrieve(self):
        response = self.get(f"/foods/{self.obj.pk}", self.obj.pk)

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertTrue(self.is_correct_serialize(self.obj, response.data))

    def test_list(self):
        response = self.get_list("/foods")

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertCorrectSerialize(response.data['results'],
                                    self.queryset,
                                    self.is_correct_serialize)

    def is_correct_serialize(self, food, serialize_data) -> bool:
        ingrs = {i.id: i for i in food.ingredients.all()}
        for ingredient_data in serialize_data.get('ingredients'):
            id = ingredient_data['url'].split('/')[-2]
            obj = ingrs[int(id)]
            is_ok = obj.name == ingredient_data['name'] and \
                    obj.calories == ingredient_data['calories']
            if not is_ok:
                return False

        return food.pk == serialize_data.get('id') and \
            food.name == serialize_data.get('name') and \
            food.description == serialize_data.get('description')

    def test_create(self):
        response = self.post("/foods/", {'name': 'pizza', 'calories': 1000})

        self.assertResponseIsJson(response, status.HTTP_201_CREATED)
        try:
            obj = self.queryset.get(pk=response.data['id'])
            self.assertTrue(self.is_correct_serialize(obj, response.data))
        except ObjectDoesNotExist:
            self.fail("object not created")

    def test_create_data_required(self):
        response = self.post("/foods/", {})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_REQUIRED})

    def test_create_name_blank(self):
        response = self.post("/foods/", {'name': self.STR_BLANK})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_BLANK})

    def test_create_name_long(self):
        response = self.post("/foods/", {'name': self.STR_LONG})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_MAX_LEN})

    def test_create_name_unique(self):
        response = self.post("/foods/", {'name': "carbonara"})

        self.assertResponseIsJson(response, status.HTTP_400_BAD_REQUEST)
        self.assertResponseHasErrorCodes(response, {'name': self.CODE_UNIQUIE})

    def test_update(self):
        response = self.put(f"/foods/{self.obj.pk}", self.obj.pk, {'name': "pizza"})
        updated_obj = self.queryset.get(pk=self.obj.pk)
        # compare without pk
        updated_obj.pk = None

        self.assertResponseIsJson(response, status.HTTP_200_OK)
        self.assertNotEqual(updated_obj, self.obj)

    def test_delete(self):
        response = self.delete(f"/foods/{self.obj.pk}", self.obj.pk)

        self.assertResponseNoContent(response)
        with self.assertRaises(ObjectDoesNotExist):
            self.queryset.get(pk=self.obj.pk)

