from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView
)
from rest_framework.permissions import IsAdminUser

from teams.models import Team
from .serializers import TaskCreateSerializer
from .services import TaskService


class TaskCreateView(CreateAPIView):
    """
    Создание задачи
    """
    permission_classes = (IsAdminUser,)
    serializer_class = TaskCreateSerializer

    def perform_create(self, serializer):
        team = get_object_or_404(Team, pk=self.kwargs['team_id'])
        self.instance = TaskService.create_task(
            created_by=self.request.user,
            team=team,
            **serializer.validated_data
        )
