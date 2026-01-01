from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    ListAPIView,
    UpdateAPIView,
    get_object_or_404
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import TokenError
from django.db.models import Q, Avg

from .serializers import (
    UserRegisterSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer
)
from .services import blacklist_tokens, blacklisted_refresh_token

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
            blacklisted_refresh_token(refresh_token)
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
    queryset = User.objects.select_related('team').annotate(
        average_rank=Avg(
            'assigned_tasks__task_evaluation__rank',
            filter=Q(assigned_tasks__status='done')
        )
    ).only(
        'email',
        'first_name',
        'last_name',
        'birthday',
        'role',
        'team',
        'created_at'
    )

    def get_object(self):
        return self.get_queryset().get(pk=self.request.user.pk)


class UserListView(ListAPIView):
    """
    Просмотр информации о пользователях. Строго для администратора
    """
    permission_classes = (IsAdminUser,)
    serializer_class = UserListSerializer
    queryset = User.objects.select_related('team').only('id', 'email', 'first_name', 'last_name', 'birthday', 'role',
                                                        'team', 'created_at')


class UserUpdateView(UpdateAPIView):
    """
    Обновление информации пользователя
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateSerializer
    queryset = User.objects.only('first_name', 'last_name', 'birthday')

    def get_object(self):
        return self.request.user


class UserDeleteView(APIView):
    """
    Удаление пользователя
    """
    permission_classes = (IsAdminUser,)

    def delete(self, request, email, *args, **kwargs):
        user = get_object_or_404(User, email=email)
        blacklist_tokens(user)
        str_user = f'Пользователь {user} успешно удалён'
        user.delete()
        return Response(
            {'detail': str_user},
            status=status.HTTP_200_OK
        )
