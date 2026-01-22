import pytest
from django.utils import timezone

from tasks.serializers import (
    TaskCreateSerializer,
    TaskUpdateSerializer,
    CommentCreateSerializer,
    CommentListSerializer,
    TaskListUserSerializer,
    TaskListAdminSerializer
)
from tasks.models import Task, Comment


@pytest.mark.serializers
@pytest.mark.django_db
class TestTaskCreateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, task_data, create_user, user_data):
        self.user = create_user(**user_data)
        task_data['assigned_to'] = self.user.email

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


@pytest.mark.serializers
@pytest.mark.django_db
class TestCommentCreateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, create_team, create_task, admin_user_data, team_data, task_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.task = create_task(created_by=self.admin, team=self.team, **task_data)

    def test_create_comment_success(self):
        """
        Тест на успешное создание комментария
        """
        serializer = CommentCreateSerializer(data={'text': 'test text'})
        assert serializer.is_valid(), serializer.errors
        assert set(serializer.data.keys()) == {'text'}
        assert serializer.validated_data['text'] == 'test text'

    def test_create_comment_without_text(self):
        """
        Тест на создание комментария без текста
        """
        serializer = CommentCreateSerializer(data={})
        assert not serializer.is_valid()
        assert 'text' in serializer.errors

    @pytest.mark.parametrize(
        'text, expected_text',
        [
            ('  test', 'test'),
            ('test   ', 'test'),
            ('  test  ', 'test'),
        ]
    )
    def test_create_comment_validation_text(self, text, expected_text):
        """
        Тест на создание комментария с валидацией текста
        """
        serializer = CommentCreateSerializer(data={'text': text})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['text'] == expected_text


@pytest.mark.serializers
@pytest.mark.django_db
class TestCommentListSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, team_data, create_team, task_data, create_task):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.task = create_task(created_by=self.admin, team=self.team, **task_data)
        self.comment = Comment.objects.create(
            author=self.admin,
            text='test',
            task=self.task,
        )

    def test_list_comment_success(self):
        """
        Тест на успешное отображение комментария
        """
        serializer = CommentListSerializer(instance=self.comment)
        expected_fields = {'author_email', 'text'}
        assert set(serializer.data.keys()) == expected_fields
        assert serializer.data['author_email'] == self.admin.email
        assert serializer.data['text'] == 'test'


@pytest.mark.serializers
@pytest.mark.django_db
class TestTaskListUserSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, team_data, create_team, task_data, create_task, create_user,
              user_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.task = create_task(created_by=self.admin, team=self.team, **task_data)
        self.user = create_user(team=self.team, **user_data)
        self.comments = []
        for i in range(3):
            self.comments.append(Comment.objects.create(
                author=self.user,
                text=f'test comment {i}',
                task=self.task,
            ))

    @pytest.fixture
    def create_serializer(self):
        return TaskListUserSerializer(instance=self.task)

    def test_list_task_display_fields(self, create_serializer):
        """
        Тест на отображение полей
        """
        serializer = create_serializer
        expected_fields = {'title', 'description', 'deadline', 'status', 'created_by', 'rank', 'created_at',
                           'updated_at', 'comments'}
        assert set(serializer.data.keys()) == expected_fields

    def test_list_task_correct_info(self, create_serializer):
        """
        Тест на корректное отображение задачи
        """
        serializer = create_serializer
        assert serializer.data['title'] == self.task.title
        assert serializer.data['description'] == self.task.description
        assert serializer.data['status'] == self.task.status
        assert len(serializer.data['comments']) == len(self.comments)

    def test_list_task_comment_correct_info(self, create_serializer):
        """
        Тест на корректное отображение комментариев у задачи
        """
        serializer = create_serializer
        assert serializer.data['comments'][0]['author_email'] == self.user.email
        assert serializer.data['comments'][-1]['text'] == self.comments[0].text


@pytest.mark.serializers
@pytest.mark.django_db
class TestTaskListAdminSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, team_data, create_team, task_data, create_task):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.task = create_task(created_by=self.admin, team=self.team, **task_data)
        self.comments = []
        for i in range(3):
            self.comments.append(Comment.objects.create(
                author=self.admin,
                text=f'test comment {i}',
                task=self.task,
            ))

    @pytest.fixture
    def create_serializer(self):
        return TaskListAdminSerializer(instance=self.task)

    def test_list_task_display_fields(self, create_serializer):
        """
        Тест на отображение полей
        """
        serializer = create_serializer
        expected_fields = {'id', 'title', 'description', 'deadline', 'status', 'assigned_to_email',
                           'assigned_to_first_name', 'assigned_to_last_name', 'team_name', 'created_at',
                           'updated_at', 'comments'}
        assert set(serializer.data.keys()) == expected_fields

    def test_list_task_correct_info(self, create_serializer):
        """
        Тест на корректное отображение задачи
        """
        serializer = create_serializer
        assert serializer.data['id'] == self.task.id
        assert serializer.data['title'] == self.task.title
        assert serializer.data['description'] == self.task.description
        assert serializer.data['status'] == self.task.status
        assert serializer.data['team_name'] == self.team.name
        assert len(serializer.data['comments']) == len(self.comments)

    def test_list_comment_correct_info(self, create_serializer):
        """
        Тест на корректное отображение комментариев у задачи
        """
        serializer = create_serializer
        assert serializer.data['comments'][0]['author_email'] == self.admin.email
        assert serializer.data['comments'][-1]['text'] == self.comments[0].text
