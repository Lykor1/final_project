from django.db.models import F, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from teams.models import Team
from .models import Task, Comment
from .serializers import (
    TaskCreateSerializer,
    TaskUpdateSerializer,
    CommentCreateSerializer,
    TaskListUserSerializer,
    TaskListAdminSerializer
)
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

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user, team_id=self.kwargs['team_id'])

    def perform_update(self, serializer):
        task = serializer.instance
        TaskService.check_update_task_permission(
            user=self.request.user,
            task=task,
            data=serializer.validated_data
        )
        TaskService.check_task_status(task=task, data=serializer.validated_data)
        serializer.save()


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
        task = get_object_or_404(Task.objects.select_related('team'), pk=self.kwargs['task_id'])
        CommentService.check_create_comment_permission(
            current_user=user,
            task=task,
        )
        serializer.save(
            task=task,
            author=user
        )


class TaskListOwnView(ListAPIView):
    """
    Просмотр списка своих задач
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskListUserSerializer

    def get_queryset(self):
        return (
            Task.objects.filter(assigned_to=self.request.user)
            .select_related('created_by')
            .prefetch_related(
                Prefetch
                    (
                    'tasks',
                    queryset=Comment.objects.only('id', 'text', 'author').select_related('author')
                )
            )
            .annotate(rank=F('task_evaluation__rank'))
            .only(
                'id',
                'title',
                'description',
                'deadline',
                'status',
                'created_by',
                'created_at',
                'updated_at',
            )
        )


class TaskListAdminView(ListAPIView):
    """
    Просмотр списка задач админом
    """
    permission_classes = (IsAdminUser,)
    serializer_class = TaskListAdminSerializer

    def get_queryset(self):
        return (
            Task.objects.filter(created_by=self.request.user)
            .select_related('assigned_to', 'team')
            .prefetch_related(
                Prefetch(
                    'tasks',
                    queryset=Comment.objects.only('id', 'text', 'author').select_related('author')
                )
            )
            .annotate(rank=F('task_evaluation__rank'))
            .only(
                'id',
                'title',
                'description',
                'deadline',
                'status',
                'assigned_to',
                'team',
                'created_at',
                'updated_at'
            )
        )
