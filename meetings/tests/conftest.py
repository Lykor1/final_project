import pytest


@pytest.fixture
def admin_user_data():
    return {
        'email': 'admin@example.com',
        'password': 'adminpassword123',
        'first_name': 'admin_first_name',
        'last_name': 'admin_last_name',
    }
