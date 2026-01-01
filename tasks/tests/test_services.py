import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from tasks.services import TaskService, CommentService
from evaluations.models import Evaluation


@pytest.mark.services
@pytest.mark.django_db
class TestCheckCreateTaskPermission:
    @pytest.fixture(autouse=True)
    def setup(self, create_user, user_data, create_superuser, admin_user_data, team_data, create_team):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)

    def test_create_task_service_success(self):
        """
        Тест на успешную проверку прав для создания задачи
        """
        TaskService.check_create_task_permission(created_by=self.admin, team=self.team, assigned_to=self.user)

    def test_create_task_service_assigned_to_without_team(self):
        """
        Тест на проверку прав исполнителя без команды
        """
        self.user.team = None
        self.user.save()
        with pytest.raises(ValidationError):
            TaskService.check_create_task_permission(created_by=self.admin, team=self.team, assigned_to=self.user)

    def test_create_task_service_not_team_created_by(self):
        """
        Тест на проверку прав не создателя команды
        """
        self.admin.team = self.team
        self.admin.save()
        with pytest.raises(PermissionDenied):
            TaskService.check_create_task_permission(created_by=self.user, team=self.team, assigned_to=self.admin)

    def test_create_task_service_not_assigned_to(self):
        TaskService.check_create_task_permission(created_by=self.admin, team=self.team)


@pytest.mark.services
@pytest.mark.django_db
class TestCheckUpdateTaskPermission:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, team_data, create_team, create_task, task_data, create_user,
              user_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.task = create_task(team=self.team, created_by=self.admin, **task_data)
        self.new_task_data = {
            'title': 'new title',
            'description': 'new description',
            'deadline': timezone.now() + timezone.timedelta(days=2),
            'status': 'in_progress',
            'assigned_to': self.user,
        }

    def test_update_task_service_success(self):
        """
        Тест на успешную проверку прав для обновления задачи
        """
        TaskService.check_update_task_permission(user=self.admin, task=self.task, data=self.new_task_data)

    def test_update_task_service_assigned_to_not_with_team(self):
        """
        Тест на проверку прав для обновления задачи с исполнителем без команды
        """
        self.user.team = None
        self.user.save()
        with pytest.raises(ValidationError):
            TaskService.check_update_task_permission(user=self.admin, task=self.task, data=self.new_task_data)

    def test_update_task_service_not_created_by(self):
        """
        Тест на проверку прав для обновления задачи не создателем задачи
        """
        with pytest.raises(PermissionDenied):
            TaskService.check_update_task_permission(user=self.user, task=self.task, data=self.new_task_data)


@pytest.mark.services
@pytest.mark.django_db
class TestCheckTaskStatus:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, team_data, create_team, task_data, create_task):
        self.admin = create_superuser(**admin_user_data)
        team = create_team(creator=self.admin, **team_data)
        task_data.update({'status': 'done'})
        self.task = create_task(created_by=self.admin, team=team, assigned_to=self.admin, **task_data)
        self.eval = Evaluation.objects.create(task=self.task, rank=5)

    def test_delete_eval_update_task_status_success(self):
        """
        Тест на успешное удаление оценки при изменении статуса выполненной задачи
        """
        assert Evaluation.objects.count() == 1
        TaskService.check_task_status(task=self.task, data={'status': 'open'})
        assert Evaluation.objects.count() == 0

    def test_delete_eval_update_task_status_not_change(self):
        """
        Тест на удаление оценки при изменении статуса выполненной задачи
        """
        assert Evaluation.objects.count() == 1
        TaskService.check_task_status(task=self.task, data={'status': 'done'})
        assert Evaluation.objects.count() == 1

    def test_delete_eval_update_task_status_without_status(self):
        """
        Тест на удаление оценки при изменении статуса выполненной задачи без изменения статуса
        """
        assert Evaluation.objects.count() == 1
        TaskService.check_task_status(task=self.task, data={})
        assert Evaluation.objects.count() == 1

    def test_delete_eval_update_task_status_without_eval(self):
        """
        Тест на удаление оценки при изменении статуса выполненной задачи без оценки
        """
        Evaluation.objects.all().delete()
        assert Evaluation.objects.count() == 0
        TaskService.check_task_status(task=self.task, data={'status': 'open'})
        assert Evaluation.objects.count() == 0


@pytest.mark.services
@pytest.mark.django_db
class TestCheckCreateCommentPermission:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_team, team_data, user_data, create_user, create_task,
              task_data):
        self.admin = create_superuser(**admin_user_data)
        team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=team, **user_data)
        self.task = create_task(team=team, created_by=self.admin, **task_data)

    def test_create_comment_team_creator_success(self):
        """
        Тест на успешное создание комментария создателем команды
        """
        CommentService.check_create_comment_permission(current_user=self.admin, task=self.task)

    def test_create_comment_team_members_success(self):
        """
        Тест на успешное создание комментария участником команды
        """
        CommentService.check_create_comment_permission(current_user=self.user, task=self.task)

    def test_create_comment_not_team_members(self):
        """
        Тест на создание комментария не участником команды
        """
        self.user.team = None
        self.user.save()
        with pytest.raises(PermissionDenied):
            CommentService.check_create_comment_permission(current_user=self.user, task=self.task)
