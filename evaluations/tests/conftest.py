import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'first_name': 'test_first',
        'last_name': 'test_last',
    }


@pytest.fixture
def admin_user_data():
    return {
        'email': 'admin@example.com',
        'password': 'adminpassword123',
        'first_name': 'admin_first',
        'last_name': 'admin_last',
    }


@pytest.fixture
def team_data():
    return {
        'name': 'test_team',
        'description': 'test_description',
    }


@pytest.fixture
def task_data():
    return {
        'title': 'test_title',
        'description': 'test_description',
        'deadline': timezone.now() + timezone.timedelta(days=4),
        'status': 'open'
    }
