from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from budgets.models import Category
from users.models import User


class TestCategory(APITestCase):
    fixtures = ['category']

    def setUp(self):
        user = User.objects.create_user(username='alamakota')
        self.client.force_authenticate(user=user)

    def test_create_category(self):
        before_count = Category.objects.count()

        url = reverse('category-list')
        data = {'name': 'New Category'}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        after_count = Category.objects.count()
        self.assertEqual(after_count - before_count, 1)
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_get_category(self):
        cat = Category.objects.get(name='Bills')
        pk = cat.pk
        nonexistent_pk = 1_000_000

        # existing category
        url = reverse('category-detail', kwargs={'pk': pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {'name': 'Bills'})

        # nonexistent category
        url = reverse('category-detail', kwargs={'pk': nonexistent_pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_category(self):
        cat = Category.objects.get(name='Bills')
        pk = cat.pk

        url = reverse('category-detail', kwargs={'pk': pk})
        data = {'name': 'Updated'}
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {'name': 'Updated'})

        updated = Category.objects.get(pk=pk)
        self.assertEqual(updated.name, 'Updated')

    def test_delete_category(self):
        cat = Category.objects.get(name='Bills')
        pk = cat.pk

        url = reverse('category-detail', kwargs={'pk': pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_categories(self):
        url = reverse('category-list')
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {'name': 'Bills'},
            {'name': 'Concerts'},
            {'name': 'Entertainment'},
            {'name': 'Groceries'},
            {'name': 'Hobby'},
        ])

    def test_categories_list_pagination(self):
        url = reverse('category-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        next_url = resp.data['next']
        self.assertIsNotNone(next_url)

        resp = self.client.get(next_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data['previous'])
        self.assertListEqual(resp.data['results'], [
            {'name': 'Income'},
            {'name': 'Shopping'},
        ])

    def test_category_filter(self):
        url = reverse('category-list')
        filtered_url = f'{url}?name=Income'
        resp = self.client.get(filtered_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {'name': 'Income'},
        ])

        partial_name_filtered_url = f'{url}?name=shop'
        resp = self.client.get(partial_name_filtered_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {'name': 'Shopping'},
        ])
