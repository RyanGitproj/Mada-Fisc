"""
Serializers d'authentification JWT.
"""
from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Serializer de validation pour le login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict) -> dict:
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Identifiants invalides. Veuillez vérifier votre nom d'utilisateur et mot de passe."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Ce compte est désactivé."
            )

        attrs["user"] = user
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer de validation pour le rafraîchissement de token."""
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """Serializer de validation pour la déconnexion."""
    refresh = serializers.CharField()
