from rest_framework.test import APIClient
import pytest


@pytest.fixture
def client():
    return APIClient()
