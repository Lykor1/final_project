import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from tasks.models import Task
from tasks.services import TaskService


@pytest.mark.services
@pytest.mark.django_db
class TestCreateTask:
    @pytest.fixture(autouse=True)
    def setup(self, create_user, user_data, create_superuser, admin_user_data, team_data, create_team):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)

    def test_create_task_service_success(self, task_data):
        """
        Тест на правильную работу сервиса для создания задачи
        """
        task = TaskService.create_task(created_by=self.admin, team=self.team, assigned_to=self.user, **task_data)
        task.refresh_from_db()
        assert Task.objects.count() == 1

    def test_create_task_service_assigned_to_without_team(self, task_data):
        """
        Тест на работу сервиса с исполнителем без команды
        """
        self.user.team = None
        self.user.save()
        with pytest.raises(ValidationError):
            TaskService.create_task(created_by=self.admin, team=self.team, assigned_to=self.user, **task_data)


@pytest.mark.services
@pytest.mark.django_db
class TestUpdateTask:
    """
    - исполнитель не в команде
    """

    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, team_data, create_team, create_task, task_data, create_user,
              user_data):
        admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.task = create_task(team=self.team, created_by=admin, **task_data)
        self.new_task_data = {
            'title': 'new title',
            'description': 'new description',
            'deadline': timezone.now() + timezone.timedelta(days=2),
            'status': 'in_progress',
            'assigned_to': self.user,
        }

    def test_update_task_service_success(self):
        """
        Тест на успешное обновление задачи сервисом
        """
        task = TaskService.update_task(task=self.task, team=self.team, **self.new_task_data)
        task.refresh_from_db()
        assert task.title == self.new_task_data['title']
        assert task.description == self.new_task_data['description']
        assert task.status == Task.Status.IN_PROGRESS

    def test_update_task_service_partial_success(self, task_data):
        """
        Тест на частичное обновление задачи сервисом
        """
        task = TaskService.update_task(task=self.task, team=self.team, title=self.new_task_data['title'])
        task.refresh_from_db()
        assert task.title == self.new_task_data['title']
        assert task.description == task_data['description']

    def test_update_task_service_assigned_to_not_with_team(self):
        """
        Тест на обновление задачи сервисом с исполнителем без команды
        """
        self.user.team = None
        self.user.save()
        with pytest.raises(ValidationError):
            TaskService.update_task(task=self.task, team=self.team, **self.new_task_data)
