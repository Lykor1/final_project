import pytest

from teams.serializers import (
    TeamCreateSerializer,
    TeamAddUserSerializer
)


@pytest.mark.serializers
@pytest.mark.django_db
class TestTeamCreateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, team_data):
        team_data.pop('creator')
        self.team_data = team_data

    def test_create_success(self):
        """
        Тест на успешное создание команды
        """
        serializer = TeamCreateSerializer(data=self.team_data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['name'] == self.team_data['name']

    @pytest.mark.parametrize(
        'name',
        [
            'ab',
            'a',
            '  ',
            ''
        ]
    )
    def test_create_invalid_name(self, name):
        """
        Тест на создание с невалидным именем
        """
        self.team_data.update({'name': name})
        serializer = TeamCreateSerializer(data=self.team_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    @pytest.mark.parametrize(
        'raw_name, expected',
        [
            ('Team', 'Team'),
            ('  Team', 'Team'),
            ('Team  ', 'Team'),
            ('  Team  ', 'Team'),
        ]
    )
    def test_create_name_strip(self, raw_name, expected):
        """
        Тест на удаление пробелов в name при создании
        """
        self.team_data.update({'name': raw_name})
        serializer = TeamCreateSerializer(data=self.team_data)
        assert serializer.is_valid()
        assert serializer.validated_data['name'] == expected

    def test_create_without_name(self):
        """
        Тест на создание без name
        """
        self.team_data.pop('name')
        serializer = TeamCreateSerializer(data=self.team_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_create_without_description(self):
        """
        Тест на создание без description
        """
        self.team_data.pop('description')
        serializer = TeamCreateSerializer(data=self.team_data)
        assert serializer.is_valid()
        assert serializer.validated_data['name'] == self.team_data['name']


class TestTeamAddUserSerializer:
    """
    - email в разном регистре
    """

    def test_valid_email(self, user_data):
        """
        Тест на валидный email
        """
        serializer = TeamAddUserSerializer(data={'user_email': user_data['email']})
        assert serializer.is_valid()
        assert serializer.validated_data['user_email'] == user_data['email']

    @pytest.mark.parametrize(
        'email',
        [
            'invalid-email',
            'test@',
            '@example.com',
            'test@.com',
            'test@com',
            ''
        ]
    )
    def test_invalid_email(self, email):
        """
        Тест на невалидный email
        """
        serializer = TeamAddUserSerializer(data={'user_email': email})
        assert not serializer.is_valid()
        assert 'user_email' in serializer.errors

    def test_missing_email(self):
        """
        Тест на отсутствие email
        """
        serializer = TeamAddUserSerializer(data={})
        assert not serializer.is_valid()
        assert 'user_email' in serializer.errors

    @pytest.mark.parametrize(
        'email, expected',
        [
            ('TEST@EXAMPLE.COM', 'test@example.com'),
            ('  test@example.com', 'test@example.com'),
            ('test@example.com  ', 'test@example.com'),
            ('  test@example.com  ', 'test@example.com'),
        ]
    )
    def test_email_valid_correctly(self, email, expected):
        """
        Тест на правильную валидацию
        """
        serializer = TeamAddUserSerializer(data={'user_email': email})
        assert serializer.is_valid()
        assert serializer.validated_data['user_email'] == expected
