import pytest
from django.utils import timezone

from tasks.serializers import TaskCreateSerializer
from tasks.models import Task


@pytest.mark.serializers
@pytest.mark.django_db
class TestTaskCreateSerializer:
    """
    - без обязательных полей
    - без необязательных полей
    """

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
