import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from tasks.models import Task
from tasks.services import TaskService, CommentService


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
class TestUpdateTask:
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
