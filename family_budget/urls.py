"""family_budget URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from budgets import views as bviews
from users import views as uviews

router = DefaultRouter()
router.register(r'budgets', bviews.BudgetViewSet, basename='budget')
router.register(r'categories', bviews.CategoryViewSet, basename='category')
router.register(r'users', uviews.UserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('api/openapi/', get_schema_view(
        title='Family Budget API',
        version='1.0.0',
    ), name='openapi-schema'),
]
