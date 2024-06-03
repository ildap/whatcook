import json

from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework.viewsets import ModelViewSet


class ModelViewSetTestCase(TestCase):
    STR_LONG = 'L' * 256
    STR_BLANK = ''

    CODE_REQUIRED = 'required'
    CODE_BLANK = 'blank'
    CODE_MAX_LEN = 'max_length'
    CODE_INVALID = 'invalid'
    CODE_UNIQUIE = 'unique'
    CODE_DOES_NOT_EXIST = 'does_not_exist'
    CODE_NO_URL_MATCH = 'no_match'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.factory = APIRequestFactory()

    def get_list(self, url):
        request = self.factory.get(url, format='json')
        force_authenticate(request, user=self.auth_user)
        return self.view(request)

    def get(self, url, pk):
        request = self.factory.get(url, format='json')
        force_authenticate(request, user=self.auth_user)
        return self.retrieve_view(request, pk=pk)

    def post(self, url, data):
        request = self.factory.post(url, data=data, format='json')
        force_authenticate(request, user=self.auth_user)
        return self.view(request)

    def put(self, url, pk, data):
        request = self.factory.put(url, data=data, format='json')
        force_authenticate(request, user=self.auth_user)
        return self.view(request, pk=pk)

    def delete(self, url, pk):
        request = self.factory.delete(url, format='json')
        force_authenticate(request, user=self.auth_user)
        return self.view(request, pk=pk)

    def assertCorrectSerialize(self, results, queryset, comparison: callable):
        ids = [r['id'] for r in results]
        objs = {obj.pk: obj for obj in queryset.filter(id__in=ids)}

        for r in results:
            is_correct = comparison(objs[r['id']], r)
            self.assertTrue(is_correct)

    def assertResponseIsJson(self, response, status_code=None):
        if status_code:
            self.assertEqual(response.status_code, status_code)

        raw = response.rendered_content
        try:
            json.loads(raw)
        except json.JSONDecodeError:
            self.fail("First argument is not valid JSON: %r" % raw)

        self.assertEqual(response.headers._store['content-type'][1], 'application/json')

    def assertResponseHasErrorCodes(self, response, error_codes: dict):
        for field_key in error_codes:
            first_code = response.data[field_key][0].code
            second_code = error_codes[field_key]
            self.assertEqual(first_code, second_code)

    def assertResponseNoContent(self, response):
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.status_text, 'No Content')
