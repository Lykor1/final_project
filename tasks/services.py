from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import Task
from evaluations.models import Evaluation


class TaskService:
    @staticmethod
    def check_create_task_permission(*, created_by, team, assigned_to=None):
        """
        Проверка прав для создания задачи
        """
        if not team.creator == created_by:
            raise PermissionDenied({'created_by': 'Создавать задачи может только создатель команды'})
        if assigned_to is not None and assigned_to.team_id != team.id:
            raise ValidationError({'assigned_to': 'Исполнитель должен быть в составе команды'})

    @staticmethod
    def check_update_task_permission(*, user, task, data):
        """
        Проверка прав для обновления задачи
        """
        if task.created_by.id != user.id:
            raise PermissionDenied({'created_by': 'Обновлять задачу может только создатель задачи'})
        if 'assigned_to' in data:
            assigned_to = data['assigned_to']
            if assigned_to is not None and assigned_to.team_id != task.team_id:
                raise ValidationError({'assigned_to': 'Исполнитель должен быть в составе команды'})

    @staticmethod
    def check_task_status(*, task, data):
        if 'status' in data:
            if task.status == Task.Status.DONE and data['status'] != Task.Status.DONE:
                Evaluation.objects.filter(task=task).delete()


class CommentService:
    @staticmethod
    def check_create_comment_permission(*, current_user, task):
        """
        Проверка прав для создания комментария
        """
        team = task.team
        if not (team.creator_id == current_user.id or team.id == current_user.team_id):
            raise PermissionDenied({'author': 'Комментировать может только создатель команды или её участники'})
