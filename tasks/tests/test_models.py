import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from tasks.models import Task, Comment


@pytest.mark.models
@pytest.mark.django_db
class TestTaskModel:
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


@pytest.mark.models
@pytest.mark.django_db
class TestCommentModel:
    @pytest.fixture(autouse=True)
    def setup(self, create_user, create_superuser, create_team, team_data, user_data, admin_user_data, create_task,
              task_data):
        self.admin = create_superuser(**admin_user_data)
        self.user = create_user(**user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.task = create_task(created_by=self.admin, assigned_to=self.user, team=self.team, **task_data)

    def test_create_comment_success(self):
        """
        Тест на успешное создание комментария
        """
        comment = Comment.objects.create(
            task=self.task,
            author=self.admin,
            text='Hello World!'
        )
        assert comment.pk is not None
        assert Comment.objects.count() == 1
        assert comment.text == 'Hello World!'
        assert comment.author == self.admin

    @pytest.mark.parametrize(
        'field',
        [
            'task',
            'author',
            'text'
        ]
    )
    def test_create_comment_without_required_fields(self, field):
        """
        Тест на создание комментария без связей
        """
        data = {
            'task': self.task,
            'author': self.admin,
            'text': 'Hello World!'
        }
        data[field] = None
        with pytest.raises(IntegrityError):
            Comment.objects.create(**data)

    def test_str_representation(self):
        """
        Тест на __str__
        """
        comment = Comment.objects.create(task=self.task, author=self.admin, text='Hello World!')
        assert str(comment) == f'{self.admin}({self.task}): Hello World!'

    def test_default_ordering(self):
        """
        Тест на сортировку
        """
        fields = Comment._meta.ordering
        assert fields == ['-created_at', 'task']
