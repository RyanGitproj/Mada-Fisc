#!/usr/bin/env python
"""Point d'entrée Django pour mada_fisc_auto."""
import os
import sys


def main() -> None:
    """Exécuter les commandes Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Êtes-vous sûr qu'il est installé et "
            "disponible dans votre variable PYTHONPATH ? Avez-vous oublié "
            "d'activer un virtualenv ?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
