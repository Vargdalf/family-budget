from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import viewsets

from users.models import User
from users.serializers import UserSerializer


class UserFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='username', lookup_expr='icontains')


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    filterset_class = UserFilter

    def get_queryset(self) -> QuerySet[User]:
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    def get_permissions(self) -> list:
        if self.request.method == 'POST':
            return []
        return super().get_permissions()
