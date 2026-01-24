import pytest
from django.urls import reverse
from django.utils import timezone

from tasks.models import Task, Comment


@pytest.mark.views
@pytest.mark.django_db
class TestTaskCreateView:
    @pytest.fixture(autouse=True)
    def setup(self, task_data, create_superuser, admin_user_data, client, create_user, user_data, create_team,
              team_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.url = reverse('tasks:create', kwargs={'team_id': self.team.id})
        self.user = create_user(team=self.team, **user_data)
        self.client = client
        task_data['assigned_to'] = self.user.id

    def test_create_task_success(self, task_data):
        """
        Тест на успешное создание задачи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 201
        assert Task.objects.count() == 1
        task = Task.objects.first()
        assert task.title == task_data['title']
        assert task.created_by == self.admin
        assert task.assigned_to == self.user

    @pytest.mark.parametrize(
        'title',
        [
            'ab',
            'a',
            '   ',
            '  ',
            ''
        ]
    )
    def test_create_task_invalid_title(self, task_data, title):
        """
        Тест на создание задачи с невалидным title
        """
        task_data.update({'title': title})
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 400
        assert 'title' in response.data

    @pytest.mark.parametrize(
        'title, expected',
        [
            ('test  ', 'test'),
            ('  test', 'test'),
            ('  test  ', 'test'),
        ]
    )
    def test_create_task_valid_title(self, task_data, title, expected):
        """
        Тест на валидацию названия задачи
        """
        self.client.force_authenticate(self.admin)
        task_data.update({'title': title})
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 201
        assert response.data['title'] == expected

    def test_create_task_team_not_found(self, task_data):
        """
        Тест на создание задачи для несуществующей команды
        """
        self.client.force_authenticate(self.admin)
        url = reverse('tasks:create', kwargs={'team_id': 999})
        response = self.client.post(url, data=task_data)
        assert response.status_code == 404
        assert 'no team matches' in str(response.data).lower()

    def test_create_task_user_without_team(self, task_data):
        """
        Тест на создание задачи с исполнителем не в команде
        """
        self.client.force_authenticate(self.admin)
        self.user.team = None
        self.user.save()
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 400
        assert 'assigned_to' in response.data

    def test_create_task_with_someone_else_team(self, task_data, create_superuser, admin_user_data):
        """
        Тест на создание задачи у чужой команды
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 403
        assert 'created_by' in response.data

    def test_create_task_not_admin(self, task_data):
        """
        Тест на создание задачи обычным пользователем
        """
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 403

    def test_create_task_unathenticated_user(self, task_data):
        """
        Тест на создание задачи анонимным пользователем
        """
        response = self.client.post(self.url, data=task_data)
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestTaskUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, create_team, team_data, create_superuser, admin_user_data, task_data, create_task, create_user,
              user_data, client):
        self.admin = create_superuser(**admin_user_data)
        team = create_team(creator=self.admin, **team_data)
        self.task = create_task(created_by=self.admin, team=team, **task_data)
        self.user = create_user(team=team, **user_data)
        self.new_task_data = {
            'title': 'new title',
            'description': 'new description',
            'deadline': timezone.now() + timezone.timedelta(days=10),
            'status': 'in_progress',
            'assigned_to': self.user.id,
        }
        self.client = client
        self.url = reverse('tasks:update', kwargs={'team_id': team.id, 'pk': self.task.pk})

    def test_update_task_success(self):
        """
        Тест на успешное обновление задачи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.url, data=self.new_task_data)
        assert response.status_code == 200
        self.task.refresh_from_db()
        assert self.task.title == self.new_task_data['title']
        assert self.task.description == self.new_task_data['description']
        assert self.task.deadline == self.new_task_data['deadline']
        assert self.task.status == Task.Status.IN_PROGRESS

    @pytest.mark.parametrize(
        'field',
        [
            'title',
            'deadline',
        ]
    )
    def test_update_task_without_required_fields(self, field):
        """
        Тест на обновление задачи без обязательных полей
        """
        self.client.force_authenticate(self.admin)
        self.new_task_data.pop(field)
        response = self.client.put(self.url, data=self.new_task_data)
        assert response.status_code == 400
        assert field in response.data

    @pytest.mark.parametrize(
        'field',
        [
            'description',
            'status',
        ]
    )
    def test_update_task_without_optional_fields(self, field):
        """
        Тест на обновление задачи без опциональных полей
        """
        self.client.force_authenticate(self.admin)
        self.new_task_data.pop(field)
        response = self.client.put(self.url, data=self.new_task_data)
        assert response.status_code == 200

    def test_partial_update_task_success(self):
        """
        Тест на частичное обновление задачи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.patch(self.url, data={'title': self.new_task_data['title']})
        assert response.status_code == 200
        self.task.refresh_from_db()
        assert self.task.title == self.new_task_data['title']

    def test_update_task_not_fount_team(self):
        """
        Тест на обновление несуществующей задачи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.put(
            reverse('tasks:update', kwargs={'team_id': 999, 'pk': self.task.pk}),
            data=self.new_task_data
        )
        assert response.status_code == 404
        assert 'no task matches' in str(response.data).lower()

    def test_update_someone_else_task(self, admin_user_data, create_superuser):
        """
        Тест на обновление чужой задачи
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.put(self.url, data=self.new_task_data)
        assert response.status_code == 404
        assert 'no task matches' in str(response.data).lower()

    def test_update_task_with_assigned_to_not_in_team(self):
        """
        Тест на обновление задачи с исполнителем вне команды
        """
        self.user.team = None
        self.user.save()
        self.client.force_authenticate(self.admin)
        response = self.client.put(self.url, data=self.new_task_data)
        assert response.status_code == 400
        assert 'исполнитель должен быть в составе команды' in str(response.data).lower()

    def test_update_task_not_admin(self):
        """
        Тест на обновление задачи обычным пользователем
        """
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=self.new_task_data)
        assert response.status_code == 403

    def test_update_task_unathenticated_user(self):
        """
        Тест на обновление задачи анонимным пользователем
        """
        response = self.client.put(self.url, data=self.new_task_data)
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestTaskDeleteView:
    @pytest.fixture(autouse=True)
    def setup(self, client, admin_user_data, create_superuser, create_team, team_data, task_data, create_task):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.task = create_task(created_by=self.admin, team=self.team, **task_data)
        self.client = client
        self.url = reverse('tasks:delete', kwargs={
            'team_id': self.team.id,
            'pk': self.task.pk
        })

    def test_delete_task_success(self):
        """
        Тест на успешное удаление задачи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.delete(self.url)
        assert response.status_code == 204

    def test_delete_task_not_team(self):
        """
        Тест на удаление задачи с несуществующей командой
        """
        self.client.force_authenticate(self.admin)
        fail_url = reverse('tasks:delete', kwargs={
            'team_id': 999,
            'pk': self.task.pk
        })
        response = self.client.delete(fail_url)
        assert response.status_code == 404

    def test_delete_task_not_task(self):
        """
        Тест на удаление несуществующей задачи
        """
        self.client.force_authenticate(self.admin)
        fail_url = reverse('tasks:delete', kwargs={
            'team_id': self.team.id,
            'pk': 999
        })
        response = self.client.delete(fail_url)
        assert response.status_code == 404

    def test_delete_someone_else_task(self, create_superuser, admin_user_data):
        """
        Тест на удаление чужой задачи
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.delete(self.url)
        assert response.status_code == 404

    def test_delete_task_not_admin(self, create_user, user_data):
        """
        Тест на удаление задачи обычным пользователем
        """
        user = create_user(**user_data)
        self.client.force_authenticate(user)
        response = self.client.delete(self.url)
        assert response.status_code == 403

    def test_delete_task_unauthenticated_user(self):
        """
        Тест на удаление задачи анонимным пользователем
        """
        response = self.client.delete(self.url)
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestCommentCreateView:
    @pytest.fixture(autouse=True)
    def setup(self, client, create_superuser, admin_user_data, create_team, team_data, create_user, user_data,
              create_task, task_data):
        self.admin = create_superuser(**admin_user_data)
        team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=team, **user_data)
        self.task = create_task(created_by=self.admin, team=team, **task_data)
        self.client = client
        self.url = reverse('tasks:add-comment', kwargs={'task_id': self.task.id})

    def test_create_comment_team_creator_success(self):
        """
        Тест на успешное создание комментария создателем команды
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'text': 'test'})
        assert response.status_code == 201
        assert response.data['text'] == 'test'
        assert Comment.objects.count() == 1
        comment = Comment.objects.first()
        assert comment.author == self.admin
        assert comment.task == self.task

    def test_create_comment_team_members_success(self):
        """
        Тест на успешное создание комментария участником команды
        """
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data={'text': 'test'})
        assert response.status_code == 201
        assert response.data['text'] == 'test'
        assert Comment.objects.count() == 1
        comment = Comment.objects.first()
        assert comment.author == self.user
        assert comment.task == self.task

    def test_create_comment_without_text(self):
        """
        Тест на создание комментария без текста
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={})
        assert response.status_code == 400
        assert 'text' in response.data

    def test_create_comment_not_team_members(self):
        """
        Тест на создание комментария не участником команды
        """
        self.user.team = None
        self.user.save()
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data={'text': 'test'})
        assert response.status_code == 403
        assert 'Комментировать может только создатель команды или её участники' in str(response.data)

    def test_create_comment_not_task(self):
        """
        Тест на создание комментария для несуществующей задачи
        """
        url = reverse('tasks:add-comment', kwargs={'task_id': 999})
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data={'text': 'test'})
        assert response.status_code == 404

    def test_create_comment_unauthenticated_user(self):
        """
        Тест на создание комментария анонимным пользователем
        """
        response = self.client.post(self.url, data={'text': 'test'})
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestTaskListOwnView:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_team, team_data, create_task, task_data, create_user,
              user_data, client):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.tasks = []
        for i in range(3):
            self.tasks.append(create_task(created_by=self.admin, team=self.team, assigned_to=self.user, **task_data))
        self.comments = []
        for t in self.tasks:
            for i in range(2):
                self.comments.append(Comment.objects.create(author=self.user, task=t, text=f'test {i}'))
        self.client = client
        self.url = reverse('tasks:own-list')

    def test_list_task_own_success(self, task_data):
        """
        Тест на успешное получение списка задач исполнителя
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data) == len(self.tasks)
        assert response.data[0]['title'] == task_data['title']
        assert response.data[1]['created_by'] == self.admin.id

    def test_list_task_own_comments(self):
        """
        Тест на успешное получение списка комментариев в списке задач исполнителя
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data[0]['comments']) == len(self.comments) / len(self.tasks)
        assert response.data[0]['comments'][0]['author'] == self.user.id
        assert response.data[1]['comments'][-1]['text'] == 'test 0'

    def test_list_task_own_not_tasks(self):
        """
        Тест на просмотр списка задач исполнителем без задач
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data == []

    def test_list_task_own_unauthenticated_user(self):
        """
        Тест на просмотр списка задач анонимным пользователем
        """
        response = self.client.get(self.url)
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestTaskListAdminView:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_team, team_data, create_task, task_data, create_user,
              user_data, client):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.tasks = []
        for i in range(3):
            self.tasks.append(create_task(created_by=self.admin, team=self.team, assigned_to=self.user, **task_data))
        self.comments = []
        for t in self.tasks:
            for i in range(2):
                self.comments.append(Comment.objects.create(author=self.admin, task=t, text=f'test {i}'))
        self.client = client
        self.url = reverse('tasks:admin-list')

    def test_list_task_admin_success(self, task_data):
        """
        Тест на успешный просмотр списка задач админа
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data) == len(self.tasks)
        assert response.data[0]['title'] == task_data['title']
        assert response.data[1]['assigned_to_email'] == self.user.email
        assert response.data[2]['team_name'] == self.team.name

    def test_list_task_admin_comments(self):
        """
        Тест на успешное получение списка комментариев в списке задач админа
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data[0]['comments']) == len(self.comments) / len(self.tasks)
        assert response.data[0]['comments'][0]['author_email'] == self.admin.email
        assert response.data[1]['comments'][-1]['text'] == 'test 0'

    def test_list_task_admin_not_tasks(self, create_superuser, admin_user_data):
        """
        Тест на получение списка задач админа без задач
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data) == 0
        assert response.data == []

    def test_list_task_admin_not_admin(self):
        """
        Тест на просмотр списка задач админа не админом
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_list_task_admin_unauthenticated_user(self):
        """
        Тест на просмотр списка задач админа анонимным пользователем
        """
        response = self.client.get(self.url)
        assert response.status_code == 401
