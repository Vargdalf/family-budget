from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from budgets.models import Budget, Entry
from users.models import User


class TestBudget(APITestCase):
    fixtures = ['user', 'budget', 'category', 'entry']

    def setUp(self):
        self.user = User.objects.get(username='dbowie')
        self.client.force_authenticate(user=self.user)

    def test_create_budget(self):
        before_count = Budget.objects.count()

        url = reverse('budget-list')
        data = {
            'name': 'New Budget',
            'entries': [
                {'category': 1, 'name': 'October', 'amount': 5000},
                {'category': 2, 'name': 'Rent', 'amount': -4000},
            ],
            'shared_with': [1],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        after_count = Budget.objects.count()
        self.assertEqual(after_count - before_count, 1)

        new_budget = Budget.objects.get(name='New Budget')
        self.assertEqual(new_budget.name, 'New Budget')
        self.assertEqual(new_budget.owner, self.user)
        self.assertIn(1, new_budget.shared_with.values_list('pk', flat=True))
        self.assertEqual(new_budget.entries.count(), 2)
        self.assertIn(Entry.objects.get(category_id=1, name='October', amount=5000), new_budget.entries.all())
        self.assertIn(Entry.objects.get(category_id=2, name='Rent', amount=-4000), new_budget.entries.all())

    def test_get_budget(self):
        owned_budget = Budget.objects.get(owner=self.user)
        shared_budget = Budget.objects.get(shared_with=self.user)
        other_budget = Budget.objects.get(pk=1)

        # Owned budget by logged in user
        url = reverse('budget-detail', kwargs={'pk': owned_budget.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {
            'name': 'The Next Day',
            'owner': 'dbowie',
            'entries': [
                {'category': 1, 'name': 'Let\'s Dance Tour', 'amount': 10000},
                {'category': 5, 'name': 'The Stars Are Out Tonight', 'amount': -500},
            ],
            'shared_with': [],
        })

        # Shared budget with logged in user
        url = reverse('budget-detail', kwargs={'pk': shared_budget.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {
            'name': 'Shared Budget',
            'owner': 'rfripp',
            'entries': [{'category': 4, 'name': 'King Crimson - Red', 'amount': -50}],
            'shared_with': [5],
        })

        # Budget not owned and not shared with logged in user
        url = reverse('budget-detail', kwargs={'pk': other_budget.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_budget(self):
        budget = Budget.objects.get(owner=self.user)
        pk = budget.pk
        new_sharer = User.objects.get(pk=4)

        url = reverse('budget-detail', kwargs={'pk': pk})
        data = {'name': 'Blackstar', 'shared_with': [new_sharer.pk]}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {
            'name': 'Blackstar',
            'owner': 'dbowie',
            'entries': [
                {'category': 1, 'name': 'Let\'s Dance Tour', 'amount': 10000},
                {'category': 5, 'name': 'The Stars Are Out Tonight', 'amount': -500},
            ],
            'shared_with': [4],
        })

        # update 1 entry
        data = {
            'entries': [
                {'category': 1, 'name': 'Let\'s Dance Tour', 'amount': 10000},
                {'category': 5, 'name': 'The Stars Are Out Tonight', 'amount': -1500},
            ]
        }
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertDictEqual(resp.data, {
            'name': 'Blackstar',
            'owner': 'dbowie',
            'entries': [
                {'category': 1, 'name': 'Let\'s Dance Tour', 'amount': 10000},
                {'category': 5, 'name': 'The Stars Are Out Tonight', 'amount': -1500},
            ],
            'shared_with': [4],
        })

        updated = Budget.objects.get(pk=pk)
        self.assertEqual(updated.name, 'Blackstar')
        self.assertIn(new_sharer, updated.shared_with.all())

    def test_delete_budget(self):
        budget = Budget.objects.get(owner=self.user)
        pk = budget.pk

        url = reverse('budget-detail', kwargs={'pk': pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_budgets(self):
        user = User.objects.get(username='kmieszala')
        self.client.force_authenticate(user=user)

        url = reverse('budget-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {
                'name': 'Painkiller',
                'owner': 'rhalford',
                'entries': [],
                'shared_with': [7],
            },
            {
                'name': 'Shared Budget',
                'owner': 'rfripp',
                'entries': [{'category': 4, 'name': 'King Crimson - Red', 'amount': -50}],
                'shared_with': [5],
            },
            {
                'name': 'Simple Budget',
                'owner': 'alamakota',
                'entries': [
                    {'category': 1, 'name': 'September', 'amount': 5000},
                    {'category': 2, 'name': 'Rent', 'amount': -2200},
                ],
                'shared_with': [],
            },
            {
                'name': 'Super One',
                'owner': 'kmieszala',
                'entries': [
                    {'category': 4, 'name': 'Concert', 'amount': -200},
                    {'category': 1, 'name': 'January', 'amount': 2500},
                    {'category': 2, 'name': 'December', 'amount': -2200},
                ],
                'shared_with': [],
            },
            {
                'name': 'The Next Day',
                'owner': 'dbowie',
                'entries': [
                    {'category': 1, 'name': 'Let\'s Dance Tour', 'amount': 10000},
                    {'category': 5, 'name': 'The Stars Are Out Tonight', 'amount': -500},
                ],
                'shared_with': [],
            },
        ])

    def test_list_budgets_not_superuser(self):
        url = reverse('budget-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {
                'name': 'Shared Budget',
                'owner': 'rfripp',
                'entries': [
                    {
                        'category': 4,
                        'name': 'King Crimson - Red',
                        'amount': -50,
                    }
                ],
                'shared_with': [5],
            },
            {
                'name': 'The Next Day',
                'owner': 'dbowie',
                'entries': [
                    {
                        'category': 1,
                        'name': 'Let\'s Dance Tour',
                        'amount': 10000,
                    },
                    {
                        'category': 5,
                        'name': 'The Stars Are Out Tonight',
                        'amount': -500,
                    }
                ],
                'shared_with': [],
            },
        ])

    def test_budgets_list_paginations(self):
        user = User.objects.get(username='kmieszala')
        self.client.force_authenticate(user=user)

        url = reverse('budget-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        next_url = resp.data['next']
        self.assertIsNotNone(next_url)

        resp = self.client.get(next_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data['previous'])
        self.assertListEqual(resp.data['results'], [
            {
                'name': 'Watershed',
                'owner': 'makerfeldt',
                'entries': [{'category': 2, 'name': 'Vocal lessons', 'amount': -100}],
                'shared_with': [],
            },
        ])

    def test_budget_filter(self):
        user = User.objects.get(username='kmieszala')
        self.client.force_authenticate(user=user)

        url = reverse('budget-list')
        filtered_url = f'{url}?name=budget'
        resp = self.client.get(filtered_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {
                'name': 'Shared Budget',
                'owner': 'rfripp',
                'entries': [{'category': 4, 'name': 'King Crimson - Red', 'amount': -50}],
                'shared_with': [5],
            },
            {
                'name': 'Simple Budget',
                'owner': 'alamakota',
                'entries': [
                    {'category': 1, 'name': 'September', 'amount': 5000},
                    {'category': 2, 'name': 'Rent', 'amount': -2200},
                ],
                'shared_with': [],
            },
        ])

        filtered_url = f'{url}?owner=mak'
        resp = self.client.get(filtered_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {
                'name': 'Simple Budget',
                'owner': 'alamakota',
                'entries': [
                    {'category': 1, 'name': 'September', 'amount': 5000},
                    {'category': 2, 'name': 'Rent', 'amount': -2200},
                ],
                'shared_with': [],
            },
            {
                'name': 'Watershed',
                'owner': 'makerfeldt',
                'entries': [{'category': 2, 'name': 'Vocal lessons', 'amount': -100}],
                'shared_with': [],
            },
        ])

        filtered_url = f'{url}?owner=mak&name=Shed'
        resp = self.client.get(filtered_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertListEqual(resp.data['results'], [
            {
                'name': 'Watershed',
                'owner': 'makerfeldt',
                'entries': [{'category': 2, 'name': 'Vocal lessons', 'amount': -100}],
                'shared_with': [],
            },
        ])
