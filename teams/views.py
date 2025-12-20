from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    get_object_or_404,
    RetrieveAPIView,
    UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model

from .models import Team
from .serializers import (
    TeamCreateSerializer,
    TeamAddUserSerializer,
    TeamUpdateUserRoleSerializer,
    TeamDetailSerializer
)
from .services import TeamService

User = get_user_model()


class TeamCreateAPIView(CreateAPIView):
    """
    Создание команды админом
    """
    queryset = Team.objects.all()
    serializer_class = TeamCreateSerializer
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TeamDeleteAPIView(DestroyAPIView):
    """
    Удаление команды админом
    """
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return Team.objects.filter(creator=self.request.user)


class TeamAddUserView(APIView):
    """
    Добавление пользователя в команду
    """
    permission_classes = (IsAdminUser,)

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, creator=self.request.user)
        serializer = TeamAddUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, email=serializer.validated_data['user_email'])
        try:
            TeamService.add_user_to_team(team, user)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'detail': 'Пользователь успешно добавлен в команду'},
            status=status.HTTP_200_OK
        )


class TeamRemoveUserView(APIView):
    """
    Удаление пользователя из команды
    """
    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = TeamAddUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, email=serializer.validated_data['user_email'])
        try:
            TeamService.remove_user_from_team(user)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'detail': 'Пользователь успешно удалён из команды'},
            status=status.HTTP_200_OK
        )


class TeamUpdateUserRoleView(APIView):
    """
    Обновление роли пользователя
    """
    permission_classes = (IsAdminUser,)

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, creator=self.request.user)
        serializer = TeamUpdateUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, email=serializer.validated_data['user_email'])
        role = serializer.validated_data['user_role']
        try:
            TeamService.change_user_role(team, user, role)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'detail': 'Роль пользователя успешно изменена'},
            status=status.HTTP_200_OK
        )


class CurrentTeamDetailView(RetrieveAPIView):
    """
    Просмотр информации о команде
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TeamDetailSerializer

    def get_object(self):
        current_user = self.request.user
        if not current_user.team:
            raise NotFound('Вы не состоите в команде')
        return current_user.team


class TeamUpdateView(UpdateAPIView):
    """
    Обновление команды
    """
    permission_classes = (IsAdminUser,)
    serializer_class = TeamCreateSerializer

    def get_queryset(self):
        return Team.objects.filter(creator=self.request.user)


"""
Просмотр всех команд
"""
