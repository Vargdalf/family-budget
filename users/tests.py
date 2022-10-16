from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class TestUser(APITestCase):
    fixtures = ['user', 'budget']

    def setUp(self):
        user = User.objects.get(username='kmieszala')
        self.client.force_authenticate(user=user)

    def test_create_user(self):
        self.client.force_authenticate(user=None)
        before_count = User.objects.count()

        url = reverse('user-list')
        data = {'username': 'new_user', 'password': 'VeryStrongPassword'}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pk = resp.data['id']

        after_count = User.objects.count()
        self.assertEqual(after_count - before_count, 1)
        new_user = User.objects.get(pk=pk)
        self.assertEqual(new_user.username, 'new_user')

    def test_get_user(self):
        user = User.objects.get(username='alamakota')
        pk = user.pk
        url = reverse('user-detail', kwargs={'pk': pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {
            'id': 2,
            'username': 'alamakota',
            'budgets': [1],
        })

    def test_get_user_not_superuser(self):
        # self user
        user = User.objects.get(username='makerfeldt')
        pk = user.pk
        self.client.force_authenticate(user=user)

        url = reverse('user-detail', kwargs={'pk': pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {
            'id': 4,
            'username': 'makerfeldt',
            'budgets': [5],
        })

        # different user
        diff_user = User.objects.get(username='dbowie')
        pk = diff_user.pk

        url = reverse('user-detail', kwargs={'pk': pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_users(self):
        url = reverse('user-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {'id': 2, 'username': 'alamakota', 'budgets': [1]},
            {'id': 5, 'username': 'dbowie', 'budgets': [4]},
            {'id': 1, 'username': 'kmieszala', 'budgets': [3]},
            {'id': 4, 'username': 'makerfeldt', 'budgets': [5]},
            {'id': 6, 'username': 'mdoctor', 'budgets': []},
        ])

    def test_list_user_not_superuser(self):
        user = User.objects.get(username='mdoctor')
        self.client.force_authenticate(user=user)

        url = reverse('user-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {'id': 6, 'username': 'mdoctor', 'budgets': []}
        ])

    def test_users_list_pagination(self):
        url = reverse('user-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        next_url = resp.data['next']
        self.assertIsNotNone(next_url)

        resp = self.client.get(next_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data['previous'])
        self.assertListEqual(resp.data['results'], [
            {'id': 3, 'username': 'rfripp', 'budgets': [2]},
            {'id': 8, 'username': 'rhalford', 'budgets': [6]},
            {'id': 7, 'username': 'stankian', 'budgets': []},
        ])

    def test_user_filter(self):
        url = reverse('user-list')
        filtered_url = f'{url}?name=rfripp'
        resp = self.client.get(filtered_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {'id': 3, 'username': 'rfripp', 'budgets': [2]},
        ])

        partial_name_filtered_url = f'{url}?name=mak'
        resp = self.client.get(partial_name_filtered_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {'id': 2, 'username': 'alamakota', 'budgets': [1]},
            {'id': 4, 'username': 'makerfeldt', 'budgets': [5]},
        ])
