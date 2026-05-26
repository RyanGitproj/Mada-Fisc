"""
Permissions personnalisées pour l'API mada_fisc_auto.
"""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Autorise l'accès uniquement aux utilisateurs staff/admin.
    Utilisé pour les opérations sensibles (modification de config, etc.).
    """

    def has_permission(self, request: object, view: object) -> bool:
        return bool(
            hasattr(request, "user")
            and request.user  # type: ignore[attr-defined]
            and request.user.is_staff  # type: ignore[attr-defined]
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Autorise l'accès si l'utilisateur est le propriétaire de la ressource
    ou s'il est admin.
    """

    def has_object_permission(self, request: object, view: object, obj: object) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False
        if getattr(user, "is_staff", False):
            return True
        # Vérifier si l'objet a un attribut 'user' ou 'owner'
        owner = getattr(obj, "user", None) or getattr(obj, "owner", None)
        return owner == user
