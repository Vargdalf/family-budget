from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    budgets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'budgets', 'password']

    def create(self, validated_data: dict) -> User:
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)
