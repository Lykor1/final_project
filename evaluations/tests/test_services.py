import pytest
from rest_framework.exceptions import ValidationError, PermissionDenied

from tasks.models import Task
from evaluations.services import EvaluationService


@pytest.mark.services
@pytest.mark.django_db
class TestCheckEvaluationPermission:
    @pytest.fixture(autouse=True)
    def setup(self, admin_user_data, create_superuser, task_data, create_task, team_data, create_team, user_data,
              create_user):
        self.admin = create_superuser(**admin_user_data)
        team = create_team(creator=self.admin, **team_data)
        self.user = create_user(**user_data)
        task_data.update({'status': 'done'})
        self.task = create_task(created_by=self.admin, team=team, assigned_to=self.user, **task_data)

    def test_create_evaluation_permission_success(self):
        """
        Тест на успешную проверку прав оценки
        """
        EvaluationService.check_create_evaluation_permission(task=self.task, current_user=self.admin)

    def test_create_evaluation_permission_not_created_by(self):
        """
        Тест на проверку прав без создателя команды
        """
        with pytest.raises(PermissionDenied):
            EvaluationService.check_create_evaluation_permission(task=self.task, current_user=self.user)

    def test_create_evaluation_permission_not_done_task(self):
        """
        Тест на проверку прав без выполненной задачи
        """
        self.task.status = Task.Status.OPEN
        self.task.save()
        with pytest.raises(ValidationError):
            EvaluationService.check_create_evaluation_permission(task=self.task, current_user=self.admin)
