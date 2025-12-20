from datetime import date

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from teams.models import Team

User = get_user_model()


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


@pytest.mark.views
@pytest.mark.django_db
class TestTeamAddUserView:
    @pytest.fixture(autouse=True)
    def setup(self, client, admin_user, regular_user, team, create_user, user_data):
        self.url = reverse('teams:add-user', kwargs={'team_id': team.id})
        self.client = client
        self.admin_user = admin_user
        self.regular_user = regular_user
        self.team = team
        data = user_data.copy()
        data.update({'email': 'another@example.com'})
        self.another_user = create_user(**data)

    def test_add_user_success(self):
        """
        Тест на успешное добавление пользователя в команду
        """
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 200
        self.regular_user.refresh_from_db()
        assert self.regular_user.team == self.team

    def test_add_user_already_in_team(self):
        """
        Тест на добавление пользователя, состоящего в команде
        """
        self.regular_user.team = self.team
        self.regular_user.save()
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 400
        assert 'уже состоит' in response.data['detail']

    @pytest.mark.parametrize(
        'data',
        [
            {},
            {'user_email': ''},
            {'user_email': 'not-a-email'}
        ]
    )
    def test_add_user_invalid_email(self, data):
        """
        Тест на добавление пользователя с невалидным email
        """
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(self.url, data=data)
        assert response.status_code == 400

    def test_add_user_not_admin(self):
        """
        Тест на добавление пользователя обычным пользователем
        """
        self.client.force_authenticate(self.regular_user)
        response = self.client.post(self.url, data={'user_email': self.another_user.email})
        assert response.status_code == 403

    def test_add_user_unauthenticated_user(self):
        """
        Тест на добавление пользователя анонимным пользователем
        """
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestTeamRemoveUserView:
    @pytest.fixture(autouse=True)
    def setup(self, client, admin_user, regular_user, team, create_user, user_data):
        self.url = reverse('teams:remove-user')
        self.client = client
        self.admin_user = admin_user
        self.regular_user = regular_user
        self.regular_user.team = team
        self.regular_user.save()

    def test_remove_user_success(self):
        """
        Тест на успешное удаление пользователя из команды
        """
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 200
        self.regular_user.refresh_from_db()
        assert self.regular_user.team is None

    def test_remove_user_without_team(self):
        """
        Тест на удаление пользователя без команды
        """
        self.regular_user.team = None
        self.regular_user.save()
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 400
        assert 'не состоит' in str(response.data)

    @pytest.mark.parametrize(
        'data',
        [
            {},
            {'user_email': ''},
            {'user_email': 'not-a-email'}
        ]
    )
    def test_remove_user_invalid_email(self, data):
        """
        Тест на удаление пользователя с невалидным email
        """
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(self.url, data=data)
        assert response.status_code == 400

    def test_remove_user_not_admin(self):
        """
        Тест на удаление пользователя обычным пользователем
        """
        self.client.force_authenticate(self.regular_user)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 403

    def test_remove_user_unauthenticated_user(self):
        """
        Тест на удаление пользователя анонимным пользователем
        """
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestTeamUpdateUserRoleView:
    @pytest.fixture(autouse=True)
    def setup(self, client, team, admin_user, regular_user):
        self.url = reverse('teams:change-role', kwargs={'team_id': team.id})
        self.client = client
        self.admin = admin_user
        regular_user.team = team
        regular_user.role = User.Role.MANAGER
        regular_user.save()
        self.regular_user = regular_user

    def test_change_role_success(self):
        """
        Тест на успешную смену роли пользователя
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email, 'user_role': User.Role.USER})
        assert response.status_code == 200
        self.regular_user.refresh_from_db()
        assert self.regular_user.role == User.Role.USER

    @pytest.mark.parametrize(
        'email, role',
        [
            ('test@', 'manag'),
            ('@example', 'superadmin'),
            ('test@com', ''),
            ('', 'administrator'),
            ('', '')
        ]
    )
    def test_change_role_invalid_data(self, email, role):
        """
        Тест на смену роли пользователя с невалидными данными
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'user_email': email, 'user_role': role})
        assert response.status_code == 400
        assert 'user_email' in str(response.data) or 'user_role' in str(response.data)

    def test_change_role_default(self):
        """
        Тест на смену роли пользователя без указания роли
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 200
        self.regular_user.refresh_from_db()
        assert self.regular_user.role == User.Role.USER

    def test_change_role_without_team(self):
        """
        Тест на смену роли пользователя без команды
        """
        self.regular_user.team = None
        self.regular_user.save()
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 400
        assert 'не состоит' in str(response.data)

    def test_change_role_in_other_team(self, create_team):
        """
        Тест на смену роли пользователя в другой команде
        """
        new_team = create_team(name='new team', creator=self.admin)
        self.regular_user.team = new_team
        self.regular_user.save()
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 400
        assert 'не состоит в данной' in str(response.data)

    def test_change_role_not_admin_user(self):
        """
        Тест на смену роли пользователя обычном пользователем
        """
        self.client.force_authenticate(self.regular_user)
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 403

    def test_change_role_unauthernticated_user(self):
        """
        Тест на смену роли пользователя анонимным пользователем
        """
        response = self.client.post(self.url, data={'user_email': self.regular_user.email})
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestCurrentTeamDetailView:
    @pytest.fixture(autouse=True)
    def setup(self, client, team, regular_user, admin_user):
        regular_user.team = team
        regular_user.save()
        self.user = regular_user
        self.client = client
        self.admin = admin_user
        self.team = team
        self.url = reverse('teams:detail')

    def test_get_current_team_success(self):
        """
        Тест на успешное получение команды
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data['name'] == self.team.name
        assert response.data['members'][0]['email'] == self.user.email
        assert response.data['creator']['email'] == self.admin.email

    def test_get_current_team_user_without_team(self):
        """
        Тест на получение команды пользователю без команды
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        assert response.status_code == 404
        assert 'не состоите в команде' in str(response.data)

    def test_get_current_team_unauthenticated_user(self):
        """
        Тест на получение команды анонимным пользователем
        """
        response = self.client.get(self.url)
        assert response.status_code == 401
        assert 'не были предоставлены' in str(response.data)


@pytest.mark.views
@pytest.mark.django_db
class TestTeamUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, client, admin_user, team):
        self.url = reverse('teams:update', kwargs={'pk': team.pk})
        self.client = client
        self.admin = admin_user
        self.team = team

    def test_update_team_success(self):
        """
        Тест на успешное обновление команды
        """
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.url, data={'name': 'new name', 'description': 'new description'})
        assert response.status_code == 200
        self.team.refresh_from_db()
        assert self.team.name == 'new name'
        assert self.team.description == 'new description'

    def test_update_team_patch(self):
        """
        Тест на успешное частичное обновление команды
        """
        self.client.force_authenticate(self.admin)
        response = self.client.patch(self.url, data={'description': 'new description'})
        assert response.status_code == 200
        self.team.refresh_from_db()
        assert self.team.name == 'test team'
        assert self.team.description == 'new description'

    def test_update_team_without_name(self):
        """
        Тест на обновление команды без поля name
        """
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.url, data={'description': 'new description'})
        assert response.status_code == 400
        assert 'name' in str(response.data)

    def test_update_team_without_description(self):
        """
        Тест на обновление команды без поля description
        """
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.url, data={'name': 'new name'})
        assert response.status_code == 200
        self.team.refresh_from_db()
        assert self.team.name == 'new name'

    @pytest.mark.parametrize(
        'name',
        [
            'ab',
            'a',
            ''
        ]
    )
    def test_update_team_invalid_name(self, name):
        """
        Тест на обновление команды с невалидным именем
        """
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.url, data={'name': name})
        assert response.status_code == 400
        assert 'name' in str(response.data)

    def test_update_someone_else_team(self, create_superuser, admin_data):
        """
        Тест на обновление чужой команды
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_data['password'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name']
        )
        self.client.force_authenticate(new_admin)
        response = self.client.put(self.url, data={'name': 'new name', 'description': 'new description'})
        assert response.status_code == 404

    def test_update_team_not_admin(self, regular_user):
        """
        Тест на обновление команды обычным пользователем
        """
        self.client.force_authenticate(regular_user)
        response = self.client.put(self.url, data={'name': 'new name', 'description': 'new description'})
        assert response.status_code == 403

    def test_update_team_unauthenticated_user(self):
        """
        Тест на обновление команды анонимным пользователем
        """
        response = self.client.put(self.url, data={'name': 'new name', 'description': 'new description'})
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestTeamListView:
    @pytest.fixture(autouse=True)
    def setup(self, client, admin_user, create_user, user_data, create_team):
        self.url = reverse('teams:list')
        self.client = client
        self.teams = []
        for i in range(3):
            self.teams.append(
                create_team(
                    name=f'{i}',
                    description=f'description{i}',
                    creator=admin_user
                )
            )
        self.users = []
        for i in range(3):
            self.users.append(
                create_user(
                    email=f'test{i}@example.com',
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    birthday=date(2000, 1, i + 1),
                    team=self.teams[i],
                )
            )
        self.admin = admin_user

    def test_team_list_success(self):
        """
        Тест на успешное получение списка команд
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data) == len(self.teams)
        assert response.data[0]['name'] == self.teams[0].name
        assert response.data[0]['creator']['email'] == self.admin.email
        assert response.data[0]['members'][0]['email'] == self.users[0].email

    def test_team_list_not_admin(self, regular_user):
        """
        Тест на получение списка команд обычным пользователем
        """
        self.client.force_authenticate(regular_user)
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_team_list_unauthenticated_user(self):
        """
        Тест на получение списка команд анонимным пользователем
        """
        response = self.client.get(self.url)
        assert response.status_code == 401
