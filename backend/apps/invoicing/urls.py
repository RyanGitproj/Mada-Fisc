"""
URLs du module facturation.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClientViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r"clients", ClientViewSet, basename="client")
router.register(r"invoices", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("", include(router.urls)),
]
