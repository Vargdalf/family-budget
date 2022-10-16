from django.conf import settings
from django.db import models


class Budget(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='shared_budgets')

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.name}'


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.name}'


class Entry(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, default='Other', blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = 'entries'
        default_related_name = 'entries'

    def __str__(self) -> str:
        return f'{self.amount} [{self.category}: {self.name}]'
