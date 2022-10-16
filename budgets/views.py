from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters
from rest_framework import viewsets

from budgets.models import Budget, Category
from budgets.permissions import IsBudgetOwnerOrSharedWith
from budgets.serializers import BudgetSerializer, CategorySerializer


class BudgetFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    owner = filters.CharFilter(field_name='owner__username', lookup_expr='icontains')

    class Meta:
        model = Budget
        fields = ['name', 'owner']


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsBudgetOwnerOrSharedWith]
    filterset_class = BudgetFilter

    def perform_create(self, serializer: BudgetSerializer) -> None:
        serializer.save(owner=self.request.user)

    def get_queryset(self) -> QuerySet[Budget]:
        user = self.request.user
        if user.is_superuser:
            return Budget.objects.all()
        return Budget.objects.filter(Q(owner=user) | Q(shared_with=user))


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
