import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from teams.models import Team


@pytest.mark.models
@pytest.mark.django_db
class TestTeamModel:
    def test_create_success(self, create_team, team_data):
        """
        Тест на успешное создание
        """
        created_team = create_team(**team_data)
        assert created_team is not None
        assert created_team.name == team_data['name']
        assert created_team.description == team_data['description']
        assert created_team.creator == team_data['creator']

    def test_create_without_name(self, team_data, create_team):
        """
        Тест на создание без названия
        """
        team_data.pop('name')
        created_team = create_team(**team_data)
        with pytest.raises(ValidationError):
            created_team.full_clean()

    def test_create_without_creator(self, team_data, create_team):
        """
        Тест на создание без создателя
        """
        team_data.pop('creator')
        with pytest.raises(IntegrityError):
            create_team(**team_data)

    def test_create_without_description(self, team_data, create_team):
        """
        Тест на создание без описания
        """
        team_data.pop('description')
        created_team = create_team(**team_data)
        assert created_team is not None
        assert created_team.name == team_data['name']
        assert created_team.creator == team_data['creator']

    def test_str_representation(self, team):
        """
        Тест на __str__
        """
        assert str(team) == team.name

    def test_default_ordering(self):
        """
        Тест на сортировку
        """
        fields = Team._meta.ordering
        assert fields == ('name', 'creator')
