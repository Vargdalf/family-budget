from django.contrib import admin

from budgets.models import Budget, Category, Entry

admin.site.register(Budget)
admin.site.register(Category)
admin.site.register(Entry)
