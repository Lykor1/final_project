import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model

from teams.models import Team

User = get_user_model()


@pytest.fixture
def today():
    return date.today()


@pytest.fixture
def adult_birthday(today):
    return today.replace(year=today.year - 25)


@pytest.fixture
def minor_birthday(today):
    return today.replace(year=today.year - 16)


@pytest.fixture
def future_birthday(today):
    return today + timedelta(days=1)


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email='admin@example.com',
        first_name='admin',
        last_name='admin',
        password='adminpassword123',
    )


@pytest.fixture
def user_data(adult_birthday):
    return {
        'email': 'test@example.com',
        'first_name': 'test',
        'last_name': 'test',
        'password': 'testpassword123',
        'password2': 'testpassword123',
        'birthday': adult_birthday
    }


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        return User.objects.create_user(**kwargs)

    return _create_user


@pytest.fixture
def user(create_user, user_data):
    return create_user(**user_data)


@pytest.fixture
def team(admin_user):
    return Team.objects.create(name='test team', creator=admin_user)
