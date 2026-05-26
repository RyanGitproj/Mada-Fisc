"""
Planification des tâches Celery Beat.
Timezone : Indian/Antananarivo (UTC+3).
"""
from celery.schedules import crontab

# Planification des tâches périodiques
CELERY_BEAT_SCHEDULE = {
    # Chaque 1er du mois à 08:00 heure Madagascar (UTC+3 = 05:00 UTC)
    "mark-overdue-invoices": {
        "task": "apps.invoicing.tasks.mark_overdue_invoices",
        "schedule": crontab(day_of_month=1, hour=5, minute=0),
    },
    # Chaque 1er du mois à 09:00 heure Madagascar (06:00 UTC)
    "send-overdue-reminders": {
        "task": "apps.invoicing.tasks.send_overdue_reminders",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),
    },
}
