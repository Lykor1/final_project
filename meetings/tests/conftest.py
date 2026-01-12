from datetime import time

import pytest
from django.utils import timezone


@pytest.fixture
def admin_user_data():
    return {
        'email': 'admin@example.com',
        'password': 'adminpassword123',
        'first_name': 'admin_first_name',
        'last_name': 'admin_last_name',
    }


@pytest.fixture
def user_data():
    return [
        {
            'email': '1@example.com',
            'password': 'testpassword123',
            'first_name': '1_first_name',
            'last_name': '1_last_name',
        },
        {
            'email': '2@example.com',
            'password': 'testpassword123',
            'first_name': '2_first_name',
            'last_name': '2_last_name'
        }
    ]


@pytest.fixture
def meeting_data():
    return {
        'topic': 'test topic',
        'date': timezone.now().date() + timezone.timedelta(days=2),
        'start_time': time(10,0),
        'end_time': time(11,0),
    }

@pytest.fixture
def team_data():
    return {
        'name': 'test_team',
        'description': 'test_description',
    }