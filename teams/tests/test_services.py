import pytest
from django.core.exceptions import ValidationError

from teams.services import TeamService
from teams.models import Team


@pytest.mark.services
@pytest.mark.django_db
class TestAddUserToTeam:
    def test_add_user_to_team_success(self, team, regular_user):
        """
        Тест на успешное добавление пользователя в команду
        """
        TeamService.add_user_to_team(team, regular_user)
        regular_user.refresh_from_db()
        assert regular_user.team == team

    def test_add_user_to_team_failure(self, team, regular_user, create_team, team_data):
        """
        Тест на добавление пользователя из другой команды в команду
        """
        TeamService.add_user_to_team(team, regular_user)
        second_team = create_team(**team_data)
        with pytest.raises(ValidationError) as exc:
            TeamService.add_user_to_team(second_team, regular_user)
        assert 'уже состоит' in str(exc.value)


@pytest.mark.services
@pytest.mark.django_db
class TestRemoveUserFromTeam:
    @pytest.fixture(autouse=True)
    def setup(self, team, regular_user):
        regular_user.team = team
        regular_user.save()

    def test_remove_user_from_team_success(self, regular_user):
        """
        Тест на успешное удаление пользователя из команды
        """
        TeamService.remove_user_from_team(regular_user)
        regular_user.refresh_from_db()
        assert regular_user.team is None

    def test_remove_user_from_team_failure(self, regular_user):
        """
        Тест на удаление пользователя без команды
        """
        TeamService.remove_user_from_team(regular_user)
        regular_user.refresh_from_db()
        with pytest.raises(ValidationError) as exc:
            TeamService.remove_user_from_team(regular_user)
        assert 'не состоит' in str(exc.value)
