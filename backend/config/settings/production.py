"""
Settings de production.
Hérite de base.py et durcit la sécurité.
"""
from .base import *  # noqa: F401,F403

DEBUG = False

# Sécurité
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# Fichiers statiques — prêt pour S3 via django-storages
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Sentri (activation conditionnelle)
if env("SENTRY_DSN", default=""):  # type: ignore[name-defined]  # noqa: F405
    import sentry_sdk
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),  # type: ignore[name-defined]  # noqa: F405
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )
