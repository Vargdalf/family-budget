import typing

from rest_framework import permissions
from rest_framework.request import Request

from budgets.models import Budget

if typing.TYPE_CHECKING:
    from budgets.views import BudgetViewSet


class IsBudgetOwnerOrSharedWith(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: 'BudgetViewSet', obj: Budget) -> bool:
        return obj.owner == request.user or request.user in obj.shared_with.all()
