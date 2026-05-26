"""
Settings de test — base de données SQLite en mémoire.
Utilisé uniquement par pytest pour les tests unitaires.
"""
from config.settings.base import *  # noqa: F401,F403

# Base de données SQLite en mémoire pour les tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Désactiver la debug toolbar pour les tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if "debug_toolbar" not in m]  # noqa: F405

# Celery synchrone
CELERY_TASK_ALWAYS_EAGER = True  # noqa: F405

# Email en console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # noqa: F405

# Password hasher rapide pour les tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
