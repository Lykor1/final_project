import pytest
from django.urls import reverse

from teams.models import Team


@pytest.mark.views
@pytest.mark.django_db
class TestTeamCreateView:
    """
    - не админ создаёт
    - аноним
    """

    @pytest.fixture(autouse=True)
    def setup(self, admin_user, regular_user, client, team_data):
        self.url = reverse('teams:create')
        self.regular_user = regular_user
        self.client = client
        self.admin_user = admin_user
        team_data.pop('creator')
        self.team_data = team_data

    def test_create_team_success(self):
        """
        Тест на успешное создание команды
        """
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(self.url, data=self.team_data)
        assert response.status_code == 201
        assert response.data['name'] == self.team_data['name']
        assert response.data['description'] == self.team_data['description']
        assert Team.objects.count() == 1
        created_team = Team.objects.first()
        assert created_team.creator == self.admin_user

    @pytest.mark.parametrize(
        'name',
        [
            'ab',
            'a',
            '   ',
            '  ',
            ''
        ]
    )
    def test_create_invalid_name(self, name):
        """
        Тест на создание команды с невалидным name
        """
        self.client.force_authenticate(self.admin_user)
        self.team_data.update({'name': name})
        response = self.client.post(self.url, data=self.team_data)
        assert response.status_code == 400
        assert 'name' in response.data

    def test_create_without_name(self):
        """
        Тест на создание команды без name
        """
        self.client.force_authenticate(self.admin_user)
        self.team_data.pop('name')
        response = self.client.post(self.url, data=self.team_data)
        assert response.status_code == 400
        assert 'name' in response.data

    def test_create_without_description(self):
        """
        Тест на создание команды без description
        """
        self.client.force_authenticate(self.admin_user)
        self.team_data.pop('description')
        response = self.client.post(self.url, data=self.team_data)
        assert response.status_code == 201
        assert response.data['name'] == self.team_data['name']

    def test_create_regular_user(self):
        """
        Тест на создание команды обычным пользователем
        """
        self.client.force_authenticate(self.regular_user)
        response = self.client.post(self.url, data=self.team_data)
        assert response.status_code == 403
        assert Team.objects.count() == 0

    def test_create_unauthenticated_user(self):
        """
        Тест на создание команды анонимным пользователем
        """
        response = self.client.post(self.url, data=self.team_data)
        assert response.status_code == 401
