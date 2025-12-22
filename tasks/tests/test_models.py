import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from tasks.models import Task


@pytest.mark.models
@pytest.mark.django_db
class TestTaskModel:
    """
    - str
    - ordering
    """

    @pytest.fixture(autouse=True)
    def setup(self, create_user, create_superuser, create_team, team_data, user_data, admin_user_data):
        self.admin = create_superuser(**admin_user_data)
        self.user = create_user(**user_data)
        self.team = create_team(creator=self.admin, **team_data)

    def test_create_task_success(self, task_data):
        """
        Тест на успешное создание записи
        """
        task = Task.objects.create(created_by=self.admin, assigned_to=self.user, team=self.team, **task_data)
        assert task.pk is not None
        assert task.created_by == self.admin
        assert task.assigned_to == self.user
        assert task.title == task_data['title']
        assert task.deadline == task_data['deadline']
        assert task.status == Task.Status.OPEN

    @pytest.mark.parametrize(
        'field',
        [
            'title',
            'deadline',
            'created_by',
            'team'
        ]
    )
    def test_create_task_without_required_fields(self, task_data, field):
        """
        Тест на создание задачи без обязательных полей
        """
        data = task_data.copy()
        data['created_by'] = self.admin
        data['assigned_to'] = self.user
        data['team'] = self.team
        data.pop(field)
        with pytest.raises(ValidationError):
            Task.objects.create(**data)

    @pytest.mark.parametrize(
        'field',
        [
            'description',
            'status',
            'assigned_to'
        ]
    )
    def test_create_task_without_optional_fields(self, task_data, field):
        """
        Тест на создание задачи без опциональных полей
        """
        data = task_data.copy()
        data['created_by'] = self.admin
        data['assigned_to'] = self.user
        data['team'] = self.team
        data.pop(field)
        task = Task.objects.create(**data)
        assert task.pk is not None

    def test_create_task_deadline_in_past(self, task_data):
        """
        Тест на задачу с дедлайном в прошлом
        """
        task_data.update({'deadline': timezone.now() - timezone.timedelta(days=1)})
        with pytest.raises(ValidationError):
            Task.objects.create(created_by=self.admin, assigned_to=self.user, team=self.team, **task_data)

    def test_str_representation(self, task_data):
        """
        Тест на __str__
        """
        task = Task.objects.create(created_by=self.admin, assigned_to=self.user, team=self.team, **task_data)
        assert str(task) == task_data['title']

    def test_default_ordering(self):
        """
        Тест на сортировку
        """
        fields = Task._meta.ordering
        assert fields == ['created_by', '-created_at']
