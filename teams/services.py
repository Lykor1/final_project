from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Team
from .tasks import notify_user_team_change

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
        notify_user_team_change(
            user_email=user.email,
            team_name=team.name,
            action='added'
        )

    @staticmethod
    @transaction.atomic
    def remove_user_from_team(user: User) -> None:
        if not user.team:
            raise ValidationError(
                'Пользователь не состоит в команде'
            )
        team_name = user.team.name
        user.team = None
        user.save(update_fields=['team'])
        notify_user_team_change(
            user_email=user.email,
            team_name=team_name,
            action='removed'
        )

    @staticmethod
    @transaction.atomic
    def change_user_role(team: Team, user: User, role: User.Role) -> None:
        if not user.team:
            raise ValidationError(
                'Пользователь не состоит в команде'
            )
        if user.team != team:
            raise ValidationError(
                'Пользователь не состоит в данной команде'
            )
        user.role = role
        user.save(update_fields=['role'])
