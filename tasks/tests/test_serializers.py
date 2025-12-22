import pytest
from django.utils import timezone

from tasks.serializers import TaskCreateSerializer, TaskUpdateSerializer
from tasks.models import Task


@pytest.mark.serializers
@pytest.mark.django_db
class TestTaskCreateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, task_data, create_user, user_data):
        self.user = create_user(**user_data)
        task_data['assigned_to'] = self.user.id

    def test_create_task_success(self, task_data):
        """
        Тест на успешное создание задачи
        """
        serializer = TaskCreateSerializer(data=task_data)
        expected_fields = {'title', 'description', 'deadline', 'status', 'assigned_to'}
        assert serializer.is_valid(), serializer.errors
        assert set(serializer.data.keys()) == expected_fields
        assert serializer.validated_data['assigned_to'] == self.user
        assert serializer.validated_data['title'] == task_data['title']
        assert serializer.validated_data['description'] == task_data['description']
        assert serializer.validated_data['status'] == Task.Status.OPEN

    @pytest.mark.parametrize(
        'data, expected',
        [
            ({'title': 'ab'}, 'title'),
            ({'title': 'a'}, 'title'),
            ({'title': ''}, 'title'),
            ({'deadline': timezone.now() - timezone.timedelta(days=1)}, 'deadline'),
            ({'status': 'cancel'}, 'status'),
        ]
    )
    def test_create_task_invalid_data(self, task_data, data, expected):
        """
        Тест на невалидные данные
        """
        task_data.update(data)
        serializer = TaskCreateSerializer(data=task_data)
        assert not serializer.is_valid()
        assert expected in serializer.errors

    def test_create_done_task_without_assigned_to(self, task_data):
        """
        Тест на создание завершённой задачи без исполнителя
        """
        task_data.update({'status': 'done', 'assigned_to': None})
        serializer = TaskCreateSerializer(data=task_data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    @pytest.mark.parametrize(
        'field',
        [
            'title',
            'deadline'
        ]
    )
    def test_create_task_without_required_fields(self, task_data, field):
        """
        Тест на создание задачи без обязательных полей
        """
        task_data.pop(field)
        serializer = TaskCreateSerializer(data=task_data)
        assert not serializer.is_valid()
        assert field in serializer.errors

    @pytest.mark.parametrize(
        'field',
        [
            'description',
            'status',
            'assigned_to',
        ]
    )
    def test_create_task_without_optional_fields(self, task_data, field):
        """
        Тест на создание задачи без опциональных полей
        """
        task_data.pop(field)
        serializer = TaskCreateSerializer(data=task_data)
        assert serializer.is_valid()


@pytest.mark.serializers
@pytest.mark.django_db
class TestTaskUpdateSerializer:
    """
    - смена дедлайна у завершённой задачи
    """

    @pytest.fixture(autouse=True)
    def setup(self, task_data, create_task, create_user, user_data, create_superuser, admin_user_data, create_team,
              team_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        user = create_user(**user_data)
        self.new_user = create_user(email='new_user', password=user_data['password'], first_name=user.first_name,
                                    last_name=user.last_name)
        self.task = create_task(created_by=self.admin, team=self.team, assigned_to=user, **task_data)
        self.new_task_data = {
            'title': 'new title',
            'description': 'new description',
            'deadline': timezone.now() + timezone.timedelta(days=7),
            'status': Task.Status.IN_PROGRESS,
            'assigned_to': self.new_user.id
        }

    def test_update_task_success(self):
        """
        Тест на успешное обновление задачи
        """
        serializer = TaskUpdateSerializer(instance=self.task, data=self.new_task_data)
        expected_fields = {'title', 'description', 'deadline', 'status', 'assigned_to'}
        assert serializer.is_valid(), serializer.errors
        assert set(serializer.data.keys()) == expected_fields
        assert serializer.validated_data['title'] == self.new_task_data['title']
        assert serializer.validated_data['status'] == Task.Status.IN_PROGRESS

    def test_update_open_task_without_assigned_to(self):
        """
        Тест на обновление статуса задачи без исполнителя
        """
        self.new_task_data.pop('assigned_to')
        serializer = TaskUpdateSerializer(instance=self.task, data=self.new_task_data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    def test_partial_update_task(self):
        """
        Тест на частичное обновление задачи
        """
        serializer = TaskUpdateSerializer(instance=self.task, data={'title': self.new_task_data['title']}, partial=True)
        assert serializer.is_valid()
        assert serializer.validated_data['title'] == self.new_task_data['title']

    def test_update_assigned_to_with_in_progress_task(self):
        """
        Тест на обновление исполнителя у задачи в работе/выполненной
        """
        self.task.status = Task.Status.DONE
        self.task.save()
        serializer = TaskUpdateSerializer(instance=self.task, data={'assigned_to': self.new_user}, partial=True)
        assert not serializer.is_valid()
        assert 'assigned_to' in serializer.errors
