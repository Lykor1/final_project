import pytest
from django.contrib.auth import get_user_model

from users.serializers import UserRegisterSerializer, UserDetailSerializer, UserListSerializer, UserUpdateSerializer

User = get_user_model()


@pytest.mark.serializers
@pytest.mark.django_db
class TestUserRegisterSerializer:
    def test_create_with_valid_data(self, user_data):
        """
        Тест на создание с валидными данными
        """
        serializer = UserRegisterSerializer(data=user_data)
        assert serializer.is_valid(), serializer.errors
        created_user = serializer.save()
        assert created_user is not None
        assert created_user.email == user_data['email']
        assert created_user.check_password(user_data['password'])
        assert created_user.first_name == user_data['first_name']
        assert created_user.last_name == user_data['last_name']
        assert 'password2' not in serializer.data

    @pytest.mark.parametrize(
        'field',
        [
            'email',
            'first_name',
            'last_name',
            'password',
            'password2'
        ]
    )
    def test_create_without_required_fields(self, user_data, field):
        """
        Тест на создание без обязательных полей
        """
        user_data.pop(field)
        serializer = UserRegisterSerializer(data=user_data)
        assert not serializer.is_valid()
        assert field in serializer.errors

    def test_create_without_optional_field(self, user_data):
        """
        Тест на создание без необязательного поля
        """
        user_data.pop('birthday')
        serializer = UserRegisterSerializer(data=user_data)
        assert serializer.is_valid()
        created_user = serializer.save()
        assert created_user is not None
        assert created_user.email == user_data['email']
        assert created_user.check_password(user_data['password'])

    def test_mismatch_passwords(self, user_data):
        """
        Тест на несовпадение password и password2
        """
        user_data.update(password2='wrongpass123')
        serializer = UserRegisterSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'password2' in serializer.errors

    @pytest.mark.parametrize(
        'password',
        [
            'test',
            '123',
            'test123'
            ''
        ]
    )
    def test_password_complexity(self, user_data, password):
        """
        Тест на сложность пароля
        """
        user_data.update(password=password, password2=password)
        serializer = UserRegisterSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors


@pytest.mark.serializers
@pytest.mark.django_db
class TestUserDetailSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, user_data, team, create_user):
        user_data.pop('password2')
        user_data['team'] = team
        self.user = create_user(**user_data)

    def test_read_valid_data(self):
        """
        Тест на верное отображение данных
        """
        serializer = UserDetailSerializer(instance=self.user)
        expected_fields = {'email', 'full_name', 'birthday', 'age', 'role', 'team_name', 'created_at'}
        assert set(serializer.data.keys()) == expected_fields
        assert serializer.data['email'] == self.user.email
        assert serializer.data['birthday'] == str(self.user.birthday)

    @pytest.mark.parametrize(
        'birthday, expected',
        [
            (True, 25),
            (False, None),
        ]
    )
    def test_get_age(self, birthday, expected):
        """
        Тест на get_age
        """
        if not birthday:
            self.user.birthday = None
        serializer = UserDetailSerializer(instance=self.user)
        assert serializer.data['age'] == expected

    @pytest.mark.parametrize(
        'team_bool, expected',
        [
            (True, 'test team'),
            (False, None),
        ]
    )
    def test_get_team_name(self, team_bool, expected):
        """
        Тест на get_team_name
        """
        if not team_bool:
            self.user.team = None
        serializer = UserDetailSerializer(instance=self.user)
        assert serializer.data['team_name'] == expected

    @pytest.mark.parametrize(
        'f_name, l_name, expected',
        [
            ('first', 'test', 'first test'),
            (' Second', 'test ', 'Second test'),
        ]
    )
    def test_get_full_name(self, f_name, l_name, expected):
        """
        Тест на get_full_name
        """
        self.user.first_name = f_name
        self.user.last_name = l_name
        serializer = UserDetailSerializer(instance=self.user)
        assert serializer.data['full_name'] == expected


@pytest.mark.serializers
@pytest.mark.django_db
class TestUserListSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, user_data, team, create_user):
        user_data.pop('password2')
        user_data['team'] = team
        self.user = create_user(**user_data)

    def test_read_valid_data(self):
        """
        Тест на верное отображение данных
        """
        serializer = UserListSerializer(instance=self.user)
        expected_fields = {'id', 'email', 'full_name', 'birthday', 'age', 'role', 'team_name', 'created_at'}
        assert set(serializer.data.keys()) == expected_fields
        assert serializer.data['id'] == self.user.id
        assert serializer.data['email'] == self.user.email
        assert serializer.data['birthday'] == str(self.user.birthday)

    @pytest.mark.parametrize(
        'birthday, expected',
        [
            (True, 25),
            (False, None),
        ]
    )
    def test_get_age(self, birthday, expected):
        """
        Тест на get_age
        """
        if not birthday:
            self.user.birthday = None
        serializer = UserListSerializer(instance=self.user)
        assert serializer.data['age'] == expected

    @pytest.mark.parametrize(
        'team_bool, expected',
        [
            (True, 'test team'),
            (False, None),
        ]
    )
    def test_get_team_name(self, team_bool, expected):
        """
        Тест на get_team_name
        """
        if not team_bool:
            self.user.team = None
        serializer = UserListSerializer(instance=self.user)
        assert serializer.data['team_name'] == expected

    @pytest.mark.parametrize(
        'f_name, l_name, expected',
        [
            ('first', 'test', 'first test'),
            (' Second', 'test ', 'Second test'),
        ]
    )
    def test_get_full_name(self, f_name, l_name, expected):
        """
        Тест на get_full_name
        """
        self.user.first_name = f_name
        self.user.last_name = l_name
        serializer = UserListSerializer(instance=self.user)
        assert serializer.data['full_name'] == expected


@pytest.mark.serializers
@pytest.mark.django_db
class TestUserUpdateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, create_user, user_data):
        user_data.pop('password2')
        self.user = create_user(**user_data)
        self.new_data = {
            'first_name': 'New',
            'last_name': 'test_data',
            'birthday': '2000-01-01',
        }

    def test_update_valid_data(self):
        """
        Тест на успешное обновление данных
        """
        serializer = UserUpdateSerializer(instance=self.user, data=self.new_data)
        assert serializer.is_valid(), serializer.errors
        new_user = serializer.save()
        new_user.refresh_from_db()
        assert new_user.first_name == self.new_data['first_name']
        assert new_user.last_name == self.new_data['last_name']

    @pytest.mark.parametrize(
        'fields',
        [
            'first_name',
            'last_name',
        ]
    )
    def test_update_without_required_fields(self, fields):
        """
        Тест на обновление без обязательных полей
        """
        self.new_data.pop(fields)
        serializer = UserUpdateSerializer(instance=self.user, data=self.new_data)
        assert not serializer.is_valid()
        assert fields in serializer.errors

    def test_update_without_optional_fields(self, user_data):
        """
        Тест на обновление без опциональных полей
        """
        self.new_data.pop('birthday')
        serializer = UserUpdateSerializer(instance=self.user, data=self.new_data)
        assert serializer.is_valid()
        new_user = serializer.save()
        new_user.refresh_from_db()
        assert new_user.birthday == user_data['birthday']

    @pytest.mark.parametrize(
        'first_name, last_name, error',
        [
            ('', 'test_data', 'first_name'),
            ('new', '', 'last_name'),
            ('', '', 'first_name')
        ]
    )
    def test_update_with_empty_fields(self, first_name, last_name, error):
        """
        Тест на пустые first_name и last_name
        """
        self.new_data.update({'first_name': first_name, 'last_name': last_name})
        serializer = UserUpdateSerializer(instance=self.user, data=self.new_data)
        assert not serializer.is_valid()
        assert error in serializer.errors

    def test_update_patch(self, user_data):
        """
        Тест на частичное обновление данных
        """
        serializer = UserUpdateSerializer(
            instance=self.user,
            data={'first_name': self.new_data['first_name']},
            partial=True
        )
        assert serializer.is_valid()
        new_user = serializer.save()
        new_user.refresh_from_db()
        assert new_user.first_name == self.new_data['first_name']
        assert new_user.last_name == user_data['last_name']
