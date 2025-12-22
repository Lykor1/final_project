import pytest
from django.urls import reverse

from tasks.models import Task


@pytest.mark.views
@pytest.mark.django_db
class TestTaskCreateView:
    """
    - чужая команда
    - обычный пользователь
    - аноним
    """

    @pytest.fixture(autouse=True)
    def setup(self, task_data, create_superuser, admin_user_data, client, create_user, user_data, create_team,
              team_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.url = reverse('tasks:create', kwargs={'team_id': self.team.id})
        self.user = create_user(team=self.team, **user_data)
        self.client = client
        task_data['assigned_to'] = self.user.id

    def test_create_task_success(self, task_data):
        """
        Тест на успешное создание задачи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 201
        assert Task.objects.count() == 1
        task = Task.objects.first()
        assert task.title == task_data['title']
        assert task.created_by == self.admin
        assert task.assigned_to == self.user

    @pytest.mark.parametrize(
        'title',
        [
            'ab',
            'a',
            '   ',
            '  ',
            ''
        ]
    )
    def test_create_task_invalid_title(self, task_data, title):
        """
        Тест на создание задачи с невалидным title
        """
        task_data.update({'title': title})
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 400
        assert 'title' in response.data

    @pytest.mark.parametrize(
        'title, expected',
        [
            ('test  ', 'test'),
            ('  test', 'test'),
            ('  test  ', 'test'),
        ]
    )
    def test_create_task_valid_title(self, task_data, title, expected):
        """
        Тест на валидацию названия задачи
        """
        self.client.force_authenticate(self.admin)
        task_data.update({'title': title})
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 201
        assert response.data['title'] == expected

    def test_create_task_team_not_found(self, task_data):
        """
        Тест на создание задачи для несуществующей команды
        """
        self.client.force_authenticate(self.admin)
        url = reverse('tasks:create', kwargs={'team_id': 999})
        response = self.client.post(url, data=task_data)
        assert response.status_code == 404
        assert 'no team matches' in str(response.data).lower()

    def test_create_task_user_without_team(self, task_data):
        """
        Тест на создание задачи с исполнителем не в команде
        """
        self.client.force_authenticate(self.admin)
        self.user.team = None
        self.user.save()
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 400
        assert 'assigned_to' in response.data

    def test_create_task_with_someone_else_team(self, task_data, create_superuser, admin_user_data):
        """
        Тест на создание задачи у чужой команды
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 403
        assert 'created_by' in response.data

    def test_create_task_not_admin(self, task_data):
        """
        Тест на создание задачи обычным пользователем
        """
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 403

    def test_create_task_unathenticated_user(self, task_data):
        """
        Тест на создание задачи анонимным пользователем
        """
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 401
