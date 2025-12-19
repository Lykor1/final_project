import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from teams.services import TeamService
from teams.models import Team

User = get_user_model()


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


@pytest.mark.services
@pytest.mark.django_db
class TestChangeUserRole:
    @pytest.fixture(autouse=True)
    def setup(self, regular_user, team):
        regular_user.team = team
        regular_user.save()

    def test_change_user_role_success(self, regular_user, team):
        """
        Тест на успешную смену роли пользователя
        """
        TeamService.change_user_role(team, regular_user, User.Role.MANAGER)
        regular_user.refresh_from_db()
        assert regular_user.role == User.Role.MANAGER

    def test_change_user_role_failure_not_team(self, regular_user, team):
        """
        Тест на смену роли пользователя без команды
        """
        regular_user.team = None
        regular_user.save()
        with pytest.raises(ValidationError) as exc:
            TeamService.change_user_role(team, regular_user, User.Role.MANAGER)
        assert 'не состоит' in str(exc.value)

    def test_change_user_role_failure_other_team(self, regular_user, team, create_team, admin_user):
        """
        Тест на смену роли пользователя в другой команде
        """
        new_team = create_team(name='new team', creator=admin_user)
        regular_user.team = new_team
        regular_user.save()
        with pytest.raises(ValidationError) as exc:
            TeamService.change_user_role(team, regular_user, User.Role.MANAGER)
        assert 'не состоит в данной' in str(exc.value)
