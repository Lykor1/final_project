from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db import transaction

from .models import Task


class TaskService:
    @staticmethod
    @transaction.atomic
    def create_task(*, created_by, team, assigned_to, **task_data):
        """
        Создание задачи с исполнителем из указанной команды
        """
        if not team.members.filter(id=assigned_to.id).exists():
            raise ValidationError({'assigned_to': 'Исполнитель должен быть в составе команды'})
        if not team.creator == created_by:
            raise PermissionDenied({'created_by': 'Создавать задачи может только создатель команды'})
        return Task.objects.create(
            created_by=created_by,
            team=team,
            assigned_to=assigned_to,
            **task_data
        )

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
