#!-*-coding:utf-8-*-
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Ingredient
from users.models import User


class CommonTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='admin',
            password='admin',
            first_name='egor',
            last_name='letov',
        )
        cls.api_client = APIClient()
        cls.token = Token.objects.create(user=cls.user)

    def setUp(self) -> None:
        self.api_client.force_authenticate(user=self.user, token=self.token)


class IngredientsViewTestCase(CommonTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.url = reverse('ingredients-list')

    def create_ing(self, **kwargs):
        data = {'measurement_unit': 'kw'}
        data.update(kwargs)
        return Ingredient.objects.create(**data)

    def test_filter(self):
        ing1 = self.create_ing(name='кабачок')
        self.create_ing(name='соль')
        self.create_ing(name='мед')

        resp = self.api_client.get(self.url, data={'name': 'каба'})

        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], ing1.id)
