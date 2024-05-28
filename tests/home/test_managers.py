from django.db.models import QuerySet
from django.contrib.postgres.search import SearchVectorExact
from django.test import TestCase

from home.managers import FoodManager, FoodQuerySet
from home.models import Food


class FoodManagerTestCase(TestCase):

    def setUp(self):
        self.foodManager = Food.objects

    def test_get_queryset(self):
        querySet = self.foodManager.get_queryset()

        self.assertIsInstance(querySet, QuerySet)
        self.assertEqual(querySet.model, Food)


class FoodQuerySetTestCase(TestCase):

    def setUp(self):
        self.queryset = Food.objects.get_queryset()

    def test_search(self):
        s_query = self.queryset.search(["test1", "test2"])
        search_vector_exact = s_query.query.where.children[0]

        self.assertIsInstance(s_query, QuerySet)
        self.assertEqual(s_query.model, Food)
        self.assertIsInstance(search_vector_exact, SearchVectorExact)
        self.assertEqual(search_vector_exact.rhs, 'test1 test2')
