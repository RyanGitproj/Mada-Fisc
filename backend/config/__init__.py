"""Package de configuration Django pour mada_fisc_auto."""
from .celery import app as celery_app

__all__ = ("celery_app",)
