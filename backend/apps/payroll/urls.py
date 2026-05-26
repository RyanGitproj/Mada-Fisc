"""
URLs du module paie.
"""
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, PayslipViewSet

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"payslips", PayslipViewSet, basename="payslip")

urlpatterns = [
    path("", include(router.urls)),
]
