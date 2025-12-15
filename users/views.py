from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegisterSerializer

User = get_user_model()


class UserRegisterView(CreateAPIView):
    """
    Регистрация пользователя
    """
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()


class UserLogoutView(APIView):
    """
    Выход из системы
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {'detail': 'Неверный refresh токен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
