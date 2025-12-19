import pytest
from django.contrib.auth import get_user_model
from datetime import date

from teams.serializers import (
    TeamCreateSerializer,
    TeamAddUserSerializer,
    TeamUpdateUserRoleSerializer,
    TeamDetailSerializer
)

User = get_user_model()


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


@pytest.mark.serializers
@pytest.mark.django_db
class TestTeamAddUserSerializer:

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


@pytest.mark.serializers
@pytest.mark.django_db
class TestTeamUpdateUserRoleSerializer:
    def test_valid_data(self, regular_user):
        """
        Тест на валидные данные
        """
        serializer = TeamUpdateUserRoleSerializer(
            data={'user_email': regular_user.email, 'user_role': User.Role.MANAGER})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['user_email'] == regular_user.email
        assert serializer.validated_data['user_role'] == User.Role.MANAGER

    @pytest.mark.parametrize(
        'email, role',
        [
            ('invalid-email', 'manager'),
            ('test@example.com', 'superadmin'),
            ('test@', 'default'),
            ('@example.com', 'u'),
            ('test@.com', 'administrator'),
            ('test@com', 'us'),
            ('', ''),
        ]
    )
    def test_invalid_data(self, email, role):
        """
        Тест на невалидные данные
        """
        serializer = TeamUpdateUserRoleSerializer(data={'user_email': email, 'user_role': role})
        assert not serializer.is_valid()
        assert 'user_email' in serializer.errors or 'user_role' in serializer.errors

    def test_empty_email(self):
        """
        Тест на отсутствие email
        """
        serializer = TeamUpdateUserRoleSerializer(data={'user_role': 'manager'})
        assert not serializer.is_valid()
        assert 'user_email' in serializer.errors

    def test_default_role(self, regular_user):
        """
        Тест на значение роли по умолчанию
        """
        regular_user.role = User.Role.MANAGER
        regular_user.save()
        serializer = TeamUpdateUserRoleSerializer(data={'user_email': regular_user.email})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['user_role'] == User.Role.USER

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


@pytest.mark.serializers
@pytest.mark.django_db
class TestTeamDetailSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_user, user_data, team):
        self.users = []
        for i in range(3):
            self.users.append(
                create_user(
                    email=f'test{i}@example.com',
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    birthday=date(2000, 1, i + 1),
                    team=team
                )
            )
        self.team = team

    @pytest.fixture
    def create_serializer(self):
        return TeamDetailSerializer(instance=self.team)

    def test_read_detail_success_fields(self, create_serializer):
        """
        Тест на правильное отображение полей
        """
        serializer = create_serializer
        expected_keys = {'name', 'description', 'creator', 'members'}
        assert set(serializer.data.keys()) == expected_keys

    def test_read_detail_success_team_data(self, create_serializer):
        """
        Тест на правильное отображение данных о команде
        """
        serializer = create_serializer
        assert serializer.data['name'] == self.team.name
        assert serializer.data['description'] == self.team.description

    def test_read_detail_success_creator_data(self, create_serializer):
        """
        Тест на правильное отображение данных о создателе команды
        """
        serializer = create_serializer
        creator_data = serializer.data['creator']
        assert creator_data['email'] == self.team.creator.email
        assert creator_data['full_name'] == f'{self.team.creator.first_name} {self.team.creator.last_name}'
        assert creator_data['role'] == self.team.creator.role
        assert 'team_name' not in creator_data

    def test_read_detail_success_members_data(self, create_serializer):
        """
        Тест на правильное отображение данных об участниках команды
        """
        serializer = create_serializer
        members_data = serializer.data['members']
        assert len(members_data) == len(self.users)
        emails = {m['email'] for m in members_data}
        expected = {user.email for user in self.users}
        assert emails == expected
        assert members_data[0]['birthday'] == '2000-01-01'
