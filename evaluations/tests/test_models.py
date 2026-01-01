import pytest
from django.core.exceptions import ValidationError

from evaluations.models import Evaluation


@pytest.mark.models
@pytest.mark.django_db
class TestEvaluationModel:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_team, team_data, create_user, user_data, create_task,
              task_data):
        self.admin = create_superuser(**admin_user_data)
        self.team = create_team(creator=self.admin, **team_data)
        self.user = create_user(team=self.team, **user_data)
        self.task = create_task(team=self.team, created_by=self.admin, assigned_to=self.user, **task_data)
        self.eval_data = {'task': self.task, 'rank': 5}

    def test_create_evaluation_success(self):
        """
        Тест на успешное создание записи оценки
        """
        eval = Evaluation.objects.create(**self.eval_data)
        assert eval.pk is not None
        assert eval.task == self.task
        assert eval.rank == 5

    @pytest.mark.parametrize(
        'field',
        [
            'task',
            'rank',
        ]
    )
    def test_create_evaluation_without_required_fields(self, field):
        """
        Тест на создание записи без обязательных полей
        """
        self.eval_data.pop(field)
        with pytest.raises(ValidationError):
            Evaluation.objects.create(**self.eval_data)

    @pytest.mark.parametrize(
        'rank',
        [
            0,
            10,
            -10,
            1000
        ]
    )
    def test_create_evaluation_invalid_rank(self, rank):
        """
        Тест на создание записи с невалидной оценкой
        """
        self.eval_data.update({'rank': rank})
        with pytest.raises(ValidationError):
            Evaluation.objects.create(**self.eval_data)

    def test_str_representation(self):
        """
        Тест на __str__
        """
        eval = Evaluation.objects.create(**self.eval_data)
        assert str(eval) == f'{eval.task.title} ({eval.task.assigned_to}): {eval.rank}'

    def test_default_ordering(self):
        """
        Тест на сортировку
        """
        fields = Evaluation._meta.ordering
        assert fields == ['task']

    def test_create_evaluation_double(self):
        """
        Тест на уникальность оценки для задачи
        """
        eval1 = Evaluation.objects.create(**self.eval_data)
        assert eval1.pk is not None
        with pytest.raises(ValidationError):
            Evaluation.objects.create(**self.eval_data)
