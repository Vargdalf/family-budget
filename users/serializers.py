from rest_framework import serializers

from budgets.models import Budget
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    budgets = serializers.PrimaryKeyRelatedField(many=True, queryset=Budget.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'budgets']
