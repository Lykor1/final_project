from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializers import UserRegisterSerializer, UserDetailSerializer

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
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh-токен отсутствует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Неверный refresh токен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDetailView(RetrieveAPIView):
    """
    Просмотр информации о пользователе
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


class UserListView(ListAPIView):
    """
    Просмотр информации о пользователях. Строго для администратора
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
