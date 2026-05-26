"""
Vues d'authentification JWT — login, refresh, logout.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, LogoutSerializer


class LoginView(APIView):
    """
    Authentification utilisateur — obtention des tokens JWT.

    POST /api/v1/auth/login/
    Body: {"username": "...", "password": "..."}
    Response: {"access": "...", "refresh": "..."}
    """
    permission_classes = [AllowAny]

    def post(self, request: object) -> Response:
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.pk,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff,
                },
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    """
    Rafraîchissement du token d'accès JWT.

    POST /api/v1/auth/refresh/
    Body: {"refresh": "..."}
    Response: {"access": "...", "refresh": "..."}
    """
    permission_classes = [AllowAny]

    def post(self, request: object) -> Response:
        from rest_framework_simplejwt.views import TokenRefreshView as _TokenRefreshView
        from rest_framework_simplejwt.serializers import TokenRefreshSerializer as _Serializer

        serializer = _Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Déconnexion — blacklister le token de rafraîchissement.

    POST /api/v1/auth/logout/
    Body: {"refresh": "..."}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: object) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = RefreshToken(serializer.validated_data["refresh"])
            refresh_token.blacklist()
        except Exception:
            return Response(
                {"error": {"code": "invalid_token", "message": "Token de rafraîchissement invalide."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Déconnexion réussie."},
            status=status.HTTP_200_OK,
        )
