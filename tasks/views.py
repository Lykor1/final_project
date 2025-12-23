from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView
)
from rest_framework.permissions import IsAdminUser

from teams.models import Team
from .models import Task
from .serializers import TaskCreateSerializer, TaskUpdateSerializer
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


class TaskUpdateView(UpdateAPIView):
    """
    Обновление задачи
    """
    permission_classes = (IsAdminUser,)
    serializer_class = TaskUpdateSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

    def perform_update(self, serializer):
        task = self.get_object()
        self.instance = TaskService.update_task(
            task=task,
            **serializer.validated_data
        )
