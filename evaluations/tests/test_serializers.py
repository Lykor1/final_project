import pytest

from evaluations.serializers import EvaluationCreateSerializer


@pytest.mark.serializers
@pytest.mark.django_db
class TestEvaluationCreateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_superuser, admin_user_data, create_team, team_data, user_data, create_user, task_data,
              create_task):
        admin = create_superuser(**admin_user_data)
        team = create_team(creator=admin, **team_data)
        user = create_user(team=team, **user_data)
        self.task = create_task(created_by=admin, assigned_to=user, team=team, **task_data)
        self.eval_data = {
            'rank': 5
        }

    def test_create_evaluation_success(self):
        """
        Тест на успешное создание оценки
        """
        serializer = EvaluationCreateSerializer(data=self.eval_data)
        expected_fields = {'rank'}
        assert serializer.is_valid(), serializer.errors
        assert set(serializer.data.keys()) == expected_fields
        assert serializer.validated_data['rank'] == 5

    def test_create_evaluation_without_rank(self):
        """
        Тест на создание оценки без оценки
        """
        self.eval_data.pop('rank')
        serializer = EvaluationCreateSerializer(data=self.eval_data)
        assert not serializer.is_valid()
        assert 'rank' in serializer.errors

    @pytest.mark.parametrize(
        'rank',
        [
            -1,
            0,
            10,
            9999,
            0.1
        ]
    )
    def test_create_evaluation_with_invalid_rank(self, rank):
        """
        Тест на создание оценки с невалидной оценкой
        """
        self.eval_data.update({'rank': rank})
        serializer = EvaluationCreateSerializer(data=self.eval_data)
        assert not serializer.is_valid()
        assert 'rank' in serializer.errors
