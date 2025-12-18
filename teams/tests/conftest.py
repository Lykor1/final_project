import pytest
from django.contrib.auth import get_user_model

from teams.models import Team

User = get_user_model()


@pytest.fixture
def create_superuser():
    def _create_superuser(**kwargs):
        return User.objects.create_superuser(**kwargs)

    return _create_superuser


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        return User.objects.create_user(**kwargs)

    return _create_user


@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'first_name': 'test',
        'last_name': 'user',
    }


@pytest.fixture
def regular_user(create_user, user_data):
    return create_user(**user_data)


@pytest.fixture
def admin_data():
    return {
        'email': 'admin@example.com',
        'password': 'adminpassword123',
        'first_name': 'admin',
        'last_name': 'user',
    }


@pytest.fixture
def admin_user(create_superuser, admin_data):
    return create_superuser(**admin_data)


@pytest.fixture
def team_data(admin_user):
    return {
        'name': 'test team',
        'description': 'test description',
        'creator': admin_user,
    }


@pytest.fixture
def create_team():
    def _create_team(**kwargs):
        return Team.objects.create(**kwargs)

    return _create_team


@pytest.fixture
def team(create_team, team_data):
    return create_team(**team_data)
