import pytest
from django.urls import reverse

from evaluations.models import Evaluation


@pytest.mark.views
@pytest.mark.django_db
class TestEvaluationCreateView:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_team, team_data, task_data, create_task, user_data,
              create_user, client):
        self.client = client
        self.admin = create_superuser(**admin_user_data)
        team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=team, **user_data)
        task_data.update({'status': 'done'})
        self.task = create_task(created_by=self.admin, team=team, assigned_to=self.user, **task_data)
        self.url = reverse('evaluations:create', kwargs={'task_id': self.task.id})

    def test_create_eval_success(self):
        """
        Тест на успешное создание оценки задачи
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'rank': 5})
        assert response.status_code == 201
        assert Evaluation.objects.count() == 1
        eval = Evaluation.objects.first()
        assert eval.task == self.task
        assert eval.rank == 5

    @pytest.mark.parametrize(
        'rank',
        [
            0,
            -1,
            6,
            10000,
            -10000
        ]
    )
    def test_create_eval_invalid_rank(self, rank):
        """
        Тест на создание оценки с невалидной оценкой
        """
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'rank': rank})
        assert response.status_code == 400
        assert 'rank' in response.data

    def test_create_eval_not_found_task(self):
        """
        Тест на создание оценки с несуществующей задачей
        """
        self.client.force_authenticate(self.admin)
        new_url = reverse('evaluations:create', kwargs={'task_id': 999})
        response = self.client.post(new_url, data={'rank': 5})
        assert response.status_code == 404
        assert 'task' in str(response.data).lower()

    @pytest.mark.parametrize(
        'status',
        [
            'open',
            'in_progress'
        ]
    )
    def test_create_eval_not_done_task(self, status):
        """
        Тест на создание оценки невыполненной задачи
        """
        self.task.status = status
        self.task.save()
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data={'rank': 5})
        assert response.status_code == 400
        assert 'Ставить оценку можно только для выполненной задачи' in str(response.data)

    def test_create_eval_not_created_by(self, create_superuser, admin_user_data):
        """
        Тест на создание оценки не создателем задачи
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.post(self.url, data={'rank': 5})
        assert response.status_code == 403
        assert 'Ставить оценки может лишь создатель задачи' in str(response.data)

    def test_create_eval_not_admin(self):
        """
        Тест на создание оценки не администратором
        """
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data={'rank': 5})
        assert response.status_code == 403

    def test_create_eval_unauthenticated_user(self):
        """
        Тест на создание оценки анонимом
        """
        response = self.client.post(self.url, data={'rank': 5})
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestEvaluationDeleteView:
    @pytest.fixture(autouse=True)
    def setup(self, admin_user_data, user_data, task_data, team_data, create_team, create_user, create_superuser,
              create_task, client):
        self.client = client
        self.admin = create_superuser(**admin_user_data)
        team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=team, **user_data)
        task_data.update({'status': 'done'})
        self.task = create_task(created_by=self.admin, team=team, assigned_to=self.user, **task_data)
        self.url = reverse('evaluations:delete', kwargs={'task_id': self.task.id})
        self.eval = Evaluation.objects.create(task=self.task, rank=5)

    def test_delete_eval_success(self):
        """
        Тест на успешное удаление оценки
        """
        self.client.force_authenticate(self.admin)
        assert Evaluation.objects.count() == 1
        response = self.client.delete(self.url)
        assert response.status_code == 204
        assert Evaluation.objects.count() == 0

    def test_delete_eval_not_found_task(self):
        """
        Тест на удаление оценки у несуществующей задачи
        """
        new_url = reverse('evaluations:delete', kwargs={'task_id': 9999})
        self.client.force_authenticate(self.admin)
        response = self.client.delete(new_url)
        assert response.status_code == 404
        assert 'task' in str(response.data).lower()

    def test_delete_eval_not_found_eval(self):
        """
        Тест на удаление несуществующей оценки
        """
        Evaluation.delete(self.eval)
        assert Evaluation.objects.count() == 0
        self.client.force_authenticate(self.admin)
        response = self.client.delete(self.url)
        assert response.status_code == 404
        assert 'evaluation' in str(response.data).lower()

    def test_delete_eval_not_created_by(self, create_superuser, admin_user_data):
        """
        Тест на удаление оценки не создателем задачи
        """
        new_admin = create_superuser(
            email='newadmin@example.com',
            password=admin_user_data['password'],
            first_name=admin_user_data['first_name'],
            last_name=admin_user_data['last_name'],
        )
        self.client.force_authenticate(new_admin)
        response = self.client.delete(self.url)
        assert response.status_code == 403
        assert 'Удалять оценки может лишь создатель задачи' in str(response.data)

    def test_delete_eval_not_admin(self):
        """
        Тест на удаление оценки не админом
        """
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url)
        assert response.status_code == 403

    def test_delete_eval_unauthenticated_user(self):
        """
        Тест на удаление оценки анонимом
        """
        response = self.client.delete(self.url)
        assert response.status_code == 401
