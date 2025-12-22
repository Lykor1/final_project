from rest_framework.test import APIClient
import pytest
from django.contrib.auth import get_user_model

from tasks.models import Task
from teams.models import Team

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_team():
    def _create_team(**kwargs):
        return Team.objects.create(**kwargs)

    return _create_team


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        return User.objects.create_user(**kwargs)

    return _create_user


@pytest.fixture
def create_superuser():
    def _create_superuser(**kwargs):
        return User.objects.create_superuser(**kwargs)

    return _create_superuser


@pytest.fixture
def create_task():
    def _create_tasks(**kwargs):
        return Task.objects.create(**kwargs)

    return _create_tasks
