from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from teams.models import Team
from .models import Task, Comment
from .serializers import TaskCreateSerializer, TaskUpdateSerializer, CommentCreateSerializer
from .services import TaskService, CommentService


class TaskCreateView(CreateAPIView):
    """
    Создание задачи
    """
    permission_classes = (IsAdminUser,)
    serializer_class = TaskCreateSerializer

    def perform_create(self, serializer):
        team = get_object_or_404(Team, pk=self.kwargs['team_id'])
        user = self.request.user
        TaskService.check_create_task_permission(
            created_by=user,
            team=team,
            assigned_to=serializer.validated_data['assigned_to']
        )
        serializer.save(
            created_by=user,
            team=team
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
        team = get_object_or_404(Team, pk=self.kwargs['team_id'])
        task = self.get_object()
        self.instance = TaskService.update_task(
            task=task,
            team=team,
            **serializer.validated_data
        )


class TaskDeleteView(DestroyAPIView):
    """
    Удаление задачи
    """
    permission_classes = (IsAdminUser,)
    queryset = Task.objects.all()

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user, team_id=self.kwargs['team_id'])


class CommentCreateView(CreateAPIView):
    """
    Создание комментария
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        CommentService.check_create_comment_permission(
            current_user=user,
            task=task,
        )
        serializer.save(
            task=task,
            author=user
        )
