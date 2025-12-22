from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from teams.models import Team
from .models import Task


class TaskService:
    @staticmethod
    @transaction.atomic
    def create_task(*, created_by, team_id, assigned_to, **task_data):
        """
        Создание задачи с исполнителем из указанной команды
        """
        team = get_object_or_404(Team, id=team_id)
        if not team.members.filter(id=assigned_to.id).exists():
            raise ValidationError('Исполнитель должен быть в составе команды')
        return Task.objects.create(
            created_by=created_by,
            team=team,
            assigned_to=assigned_to,
            **task_data
        )
