from django.db.models import QuerySet, ObjectDoesNotExist
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from home.views import FoodViewSet
from home.models import Food
from abc import ABCMeta, abstractmethod


class ModelViewSetTestMixin:
    """
        Mixin class for testing "crud" methods from ModelViewSet subclasses
    """
    __metaclass__ = ABCMeta

    def setUp(self):
        self.factory = APIRequestFactory()
        self.detail_view = self.get_viewset_class().as_view({"get": "retrieve"})
        self.view = self.get_viewset_class().as_view({"get": "list", "post": "create",
                                                      "put": "update", "delete": "destroy"})

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
                    "no valid data": {"field name1": "value", "field name2": ""},
                    "error codes":   {"field name2": "blank"}
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
        request = self.factory.get(self.get_url(), format="json")
        response = self.view(request)
        model_count = self.get_queryset().count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], model_count)

    def test_create_no_valid(self):
        for testcase in self.validation_testcases():
            data = testcase["no valid data"]
            error_codes = testcase["error codes"]
            request = self.factory.post(self.get_url(), data=data, format="json")
            response = self.view(request)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            for field_key in error_codes:
                first_code = response.data[field_key][0].code
                second_code = error_codes[field_key]
                self.assertEqual(first_code, second_code)

    def test_create_valid(self):
        request = self.factory.post(self.get_url(),
                                    data=self.get_valid_data(),
                                    format="json")
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:
            self.get_queryset().get(id=response.data["id"])
        except ObjectDoesNotExist:
            self.fail("object not created")

    def test_retrieve(self):
        obj = self.get_queryset().first()
        request = self.factory.get(self.get_url() + str(obj.pk), format="json")
        response = self.detail_view(request, pk=obj.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if not self.is_correct_serialize(obj, response.data):
            self.fail("no correct serialization")

    def test_update(self):
        obj = self.get_queryset().first()
        request = self.factory.put(self.get_url() + str(obj.pk),
                                   data=self.get_valid_data(),
                                   format="json")
        response = self.view(request, pk=obj.pk)
        updated_obj = self.get_queryset().first()
        # for comparing without pk
        updated_obj.pk = None

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(updated_obj, obj)

    def test_delete(self):
        obj = self.get_queryset().first()
        request = self.factory.delete(self.get_url() + str(obj.pk), format="json")
        response = self.view(request, pk=obj.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            self.get_queryset().get(pk=obj.pk)


class FoodViewSetTest(ModelViewSetTestMixin, TestCase):
    fixtures = ["data.json"]

    # Implemented abstract methods
    def get_viewset_class(self) -> ModelViewSet.__class__:
        return FoodViewSet

    def get_url(self):
        return "/foods/"

    def get_queryset(self) -> QuerySet:
        return Food.objects.get_queryset()

    def validation_testcases(self):
        long_string = "L" * 256
        blank_string = ""
        return [
            {
                "no valid data": {"name": blank_string, "description": long_string},
                "error codes": {"name": "blank", "description": "max_length"}
            }
        ]

    def get_valid_data(self) -> dict:
        return {"name": "pizza"}

    def is_correct_serialize(self, model_object, serialize_data) -> bool:
        return model_object.id == serialize_data.get("id") and \
               model_object.name == serialize_data.get("name") and \
               model_object.description == serialize_data.get("description")

    # Test cases
    def test_create_unique(self):
        request = self.factory.post(self.get_url(),
                                    data={"name": "carbonara"}, format="json")
        response = self.view(request)

        self.assertEqual(response.data["name"][0].code, "unique")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
