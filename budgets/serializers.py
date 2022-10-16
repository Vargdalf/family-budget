from rest_framework import serializers

from budgets.models import Budget, Category, Entry
from users.models import User


class BudgetSerializer(serializers.ModelSerializer):
    entries = serializers.PrimaryKeyRelatedField(many=True, queryset=Entry.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    shared_with = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Budget
        fields = ['name', 'owner', 'entries', 'shared_with']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']
