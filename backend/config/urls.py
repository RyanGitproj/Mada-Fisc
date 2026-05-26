"""
URL racine de l'API mada_fisc_auto.
Tous les endpoints sont préfixés par /api/v1/.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/payroll/", include("apps.payroll.urls")),
    path("api/v1/invoicing/", include("apps.invoicing.urls")),
    path("api/v1/dashboard/", include("apps.core.dashboard_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
