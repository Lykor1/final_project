from django.core.exceptions import ValidationError
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
        return Task.objects.create(
            created_by=created_by,
            team=team,
            assigned_to=assigned_to,
            **task_data
        )
