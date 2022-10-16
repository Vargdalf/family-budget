from decimal import Decimal

from django.contrib import admin
from django.contrib.admin import register
from django.db.models import Sum

from budgets.models import Budget, Category, Entry

admin.site.register(Category)


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 0


@register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'budget_sum')
    inlines = [
        EntryInline,
    ]

    @admin.display(description='Budget Sum')
    def budget_sum(self, obj: Budget) -> Decimal:
        return obj.entries.aggregate(Sum('amount'))['amount__sum']
