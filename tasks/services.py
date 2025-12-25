from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied


class TaskService:
    @staticmethod
    def check_create_task_permission(*, created_by, team, assigned_to=None):
        """
        Проверка прав для создания задачи
        """
        if not team.creator == created_by:
            raise PermissionDenied({'created_by': 'Создавать задачи может только создатель команды'})
        if assigned_to is not None and not team.members.filter(id=assigned_to.id).exists():
            raise ValidationError({'assigned_to': 'Исполнитель должен быть в составе команды'})

    @staticmethod
    @transaction.atomic
    def update_task(*, task, team, **task_data):
        """
        Обновление задачи
        """
        if 'assigned_to' in task_data:
            assigned_to = task_data['assigned_to']
            if not team.members.filter(id=assigned_to.id).exists():
                raise ValidationError({'assigned_to': 'Исполнитель должен быть в составе команды'})
        for field, value in task_data.items():
            setattr(task, field, value)
        task.save()
        return task


class CommentService:
    @staticmethod
    def check_create_comment_permission(*, current_user, task):
        """
        Проверка прав для создания комментария
        """
        team = task.team
        if not (team.creator == current_user or team.members.filter(id=current_user.id).exists()):
            raise PermissionDenied({'author': 'Комментировать может только создатель команды или её участники'})
