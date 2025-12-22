import pytest
from django.core.exceptions import ValidationError

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
