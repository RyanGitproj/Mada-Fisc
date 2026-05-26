"""
Settings de développement.
Hérite de base.py et active le mode debug.
"""
from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Afficher les erreurs DRF en détail
REST_FRAMEWORK = {  # type: ignore[assignment]
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.core.exception_handler.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DATETIME_FORMAT": "%d/%m/%Y %H:%M",
    "DATE_FORMAT": "%d/%m/%Y",
}

# Debug toolbar
INSTALLED_APPS += [  # type: ignore[operator]
    "debug_toolbar",
]

MIDDLEWARE += [  # type: ignore[operator]
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# Celery en mode synchrone pour faciliter le débogage
CELERY_TASK_ALWAYS_EAGER = True

# Email en console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
