from django_filters import rest_framework as filters
from rest_framework import viewsets

from users.models import User
from users.serializers import UserSerializer


class UserFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='username', lookup_expr='icontains')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
