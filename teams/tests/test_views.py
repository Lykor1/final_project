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


@pytest.mark.views
@pytest.mark.django_db
class TestTeamDeleteView:
    @pytest.fixture(autouse=True)
    def setup(self, client, admin_user, team, create_superuser, admin_data):
        self.url = reverse('teams:delete', kwargs={'pk': team.pk})
        self.client = client
        self.admin_user = admin_user
        another_admin_data = admin_data.copy()
        another_admin_data.update({'email': 'anotheradmin@example.com'})
        self.another_admin = create_superuser(**another_admin_data)

    def test_delete_team_success(self):
        """
        Тест на успешное удаление команды
        """
        self.client.force_authenticate(self.admin_user)
        response = self.client.delete(self.url)
        assert response.status_code == 204
        assert Team.objects.count() == 0

    def test_delete_someone_else_team(self, create_team, team_data):
        """
        Тест на удаление чужой команды
        """
        self.client.force_authenticate(self.another_admin)
        response = self.client.delete(self.url)
        assert response.status_code == 404
        assert Team.objects.filter(creator=self.admin_user).exists()

    def test_delete_team_regular_user(self, regular_user):
        """
        Тест на удаление команды обычным пользователем
        """
        self.client.force_authenticate(regular_user)
        response = self.client.delete(self.url)
        assert response.status_code == 403
        assert Team.objects.count() == 1

    def test_delete_team_members(self, regular_user, team):
        """
        Тест на удаление команды участником (обычным пользователем)
        """
        regular_user.team = team
        regular_user.save()
        self.client.force_authenticate(regular_user)
        response = self.client.delete(self.url)
        assert response.status_code == 403
        assert Team.objects.count() == 1

    def test_delete_team_members_admin(self, team):
        """
        Тест на удаление команды участником (админом)
        """
        self.another_admin.team = team
        self.another_admin.save()
        self.client.force_authenticate(self.another_admin)
        response = self.client.delete(self.url)
        assert response.status_code == 404
        assert Team.objects.count() == 1

    def test_delete_team_unauthenticated_user(self):
        """
        Тест на удаление команды анонимом
        """
        response = self.client.delete(self.url)
        assert response.status_code == 401
        assert Team.objects.count() == 1
