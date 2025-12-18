from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Team

User = get_user_model()


class TeamService:
    @staticmethod
    @transaction.atomic
    def add_user_to_team(team: Team, user: User) -> None:
        if user.team:
            raise ValidationError(
                'Пользователь уже состоит в другой команде'
            )
        user.team = team
        user.save(update_fields=['team'])
