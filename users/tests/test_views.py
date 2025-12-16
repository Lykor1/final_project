import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.views
@pytest.mark.django_db
class TestUserRegisterView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse('users:register')

    def test_register_success(self, client, user_data):
        """
        Тест на успешную регистрацию
        """
        response = client.post(self.url, data=user_data)
        assert response.status_code == 201
        assert response.data['email'] == user_data['email']
        assert response.data['first_name'] == user_data['first_name']
        assert response.data['last_name'] == user_data['last_name']
        assert User.objects.count() == 1
        created_user = User.objects.get(email=user_data['email'])
        assert created_user.check_password(user_data['password'])

    @pytest.mark.parametrize(
        'email, password, password2',
        [
            ('test', 'testpassword123', 'testpassword123'),
            ('test@example.com', 'test', 'test'),
            ('test@example.com', '123', '123'),
            ('test@example.com', 'testpassword123', '123'),
        ]
    )
    def test_register_invalid_data(self, client, user_data, email, password, password2):
        """
        Тест на регистрацию с невалидными данными
        """
        user_data.update({'email': email, 'password': password, 'password2': password2})
        response = client.post(self.url, data=user_data)
        assert response.status_code == 400
        assert 'email' or 'password' in response.data

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
    def test_register_without_required_fields(self, client, user_data, field):
        """
        Тест на отсутствие обязательных полей
        """
        user_data.pop(field)
        response = client.post(self.url, data=user_data)
        assert response.status_code == 400
        assert field in response.data

    def test_register_without_optional_fields(self, client, user_data):
        """
        Тест на отсутствие необязательных полей
        """
        user_data.pop('birthday')
        response = client.post(self.url, data=user_data)
        assert response.status_code == 201
        assert response.data['email'] == user_data['email']
        assert response.data['first_name'] == user_data['first_name']
        assert User.objects.count() == 1
        created_user = User.objects.first()
        assert created_user.check_password(user_data['password'])

    def test_duplicate_user(self, user_data, client):
        """
        Тест на создание дубликата пользователя
        """
        response1 = client.post(self.url, data=user_data)
        assert response1.status_code == 201
        assert response1.data['email'] == user_data['email']
        response2 = client.post(self.url, data=user_data)
        assert response2.status_code == 400
        assert 'email' in response2.data


@pytest.mark.views
@pytest.mark.django_db
class TestTokenObtainPairView:
    @pytest.fixture(autouse=True)
    def setup(self, user_data, create_user, client):
        user_data.pop('password2')
        self.user = create_user(**user_data)
        user_data.pop('birthday')
        user_data.pop('first_name')
        user_data.pop('last_name')
        self.data = user_data
        self.url = reverse('users:login')
        self.client = client

    def test_login_success(self):
        """
        Тест на успешный логин
        """
        response = self.client.post(self.url, data=self.data)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert not 'password' in response.data

    @pytest.mark.parametrize(
        'fields',
        [
            'email',
            'password'
        ]
    )
    def test_login_without_required_fields(self, fields):
        """
        Тест на логин без обязательных полей
        """
        self.data.pop(fields)
        response = self.client.post(self.url, data=self.data)
        assert response.status_code == 400
        assert fields in response.data

    @pytest.mark.parametrize(
        'email, password',
        [
            ('test@example.com', '123'),
            ('test', 'testpassword123'),
        ]
    )
    def test_login_invalid_data(self, email, password):
        """
        Тест на логин с невалидными данными
        """
        self.data.update({'email': email, 'password': password})
        response = self.client.post(self.url, data=self.data)
        assert response.status_code == 401
        assert 'не найдено активной учетной записи' in str(response.data).lower()

    @pytest.mark.parametrize(
        'email, password',
        [
            ('test@example.com', ''),
            ('', 'testpassword123'),
        ]
    )
    def test_login_with_empty_email_or_password(self, email, password):
        """
        Тест на логин c пустыми email/password
        """
        self.data.update({'email': email, 'password': password})
        response = self.client.post(self.url, data=self.data)
        assert response.status_code == 400
        assert 'email' in response.data or 'password' in response.data


@pytest.mark.views
@pytest.mark.django_db
class TestTokenRefreshView:
    @pytest.fixture(autouse=True)
    def setup(self, client, create_user, user_data):
        user_data.pop('password2')
        self.data = user_data
        self.user = create_user(**user_data)
        self.url = reverse('users:refresh')
        self.client = client
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_refresh_success(self):
        """
        Тест на успешное обновление refresh-токена
        """
        response = self.client.post(self.url, data={'refresh': self.refresh_token})
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_refresh_invalid_token(self):
        """
        Тест на обновление с невалидным токеном
        """
        response = self.client.post(self.url, data={'refresh': 'invalidToken'})
        assert response.status_code == 401
        assert 'detail' in response.data

    def test_refresh_missing_token(self):
        """
        Тест на обновление без токена
        """
        response = self.client.post(self.url, data={})
        assert response.status_code == 400
        assert 'refresh' in response.data


@pytest.mark.views
@pytest.mark.django_db
class TestUserLogoutView:

    @pytest.fixture(autouse=True)
    def setup(self, client, create_user, user_data):
        user_data.pop('password2')
        self.user = create_user(**user_data)
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.client = client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        self.url = reverse('users:logout')

    def test_logout_success(self):
        """
        Тест на успешный выход
        """
        response = self.client.post(self.url, data={'refresh': self.refresh_token})
        print(response.data)
        assert response.status_code == 204

    def test_logout_invalid_token(self):
        """
        Тест на выход с неверным refresh-токеном
        """
        response = self.client.post(self.url, data={'refresh': 'invalidToken'})
        assert response.status_code == 400
        assert 'detail' in response.data

    def test_logout_missing_token(self):
        """
        Тест на выход без токена
        """
        response = self.client.post(self.url, data={})
        assert response.status_code == 400
        assert 'detail' in response.data

    def test_logout_unauthenticated(self):
        """
        Тест на выход неавторизованного пользователя
        """
        self.client.credentials()
        response = self.client.post(self.url, data={'refresh': self.refresh_token})
        assert response.status_code == 401


@pytest.mark.views
@pytest.mark.django_db
class TestUserDetailView:
    @pytest.fixture(autouse=True)
    def setup(self, client, create_user, user_data, team):
        self.url = reverse('users:detail')
        user_data.pop('password2')
        user_data['team'] = team
        self.user = create_user(**user_data)
        self.client = client

    def test_read_detail_success(self):
        """
        Тест на успешный просмотр информации о пользователе
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        expected_fields = {'email', 'full_name', 'birthday', 'age', 'role', 'team_name', 'created_at'}
        assert set(response.data.keys()) == expected_fields
        assert response.data['email'] == self.user.email
        assert response.data['full_name'] == f'{self.user.first_name} {self.user.last_name}'
        assert 'password' not in response.data

    def test_read_detail_unauthenticated(self):
        """
        Тест на просмотр анонимного пользователя
        """
        response = self.client.get(self.url)
        assert response.status_code == 401
        assert 'учетные данные не были предоставлены' in str(response.data).lower()

    def test_read_detail_with_current_user(self, create_user):
        """
        Тест на просмотр именно текущего пользователя
        """
        data = {
            'email': 'other@example.com',
            'password': self.user.password,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name
        }
        other_user = create_user(**data)
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert not response.data['email'] == 'other@example.com'


@pytest.mark.views
@pytest.mark.django_db
class TestUserListView:
    """
    - анонимный пользователь
    - не админ
    """

    @pytest.fixture(autouse=True)
    def setup(self, client, create_user, user_data, team, admin_user):
        self.url = reverse('users:list')
        self.admin = admin_user
        self.users = []
        for i in range(5):
            email = f"{user_data['email'].split('@')[0]}{i}@example.com"
            first_name = f"{user_data['first_name']}{i}"
            last_name = f"{user_data['last_name']}{i}"
            self.users.append(
                create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    birthday=user_data['birthday'],
                    team=team,
                )
            )
        self.client = client

    def test_read_list_success(self):
        """
        Тест на успешный просмотр списка пользователей
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert User.objects.count() == 6
        expected_fields = {'id', 'email', 'full_name', 'birthday', 'age', 'role', 'team_name', 'created_at'}
        assert set(response.data[0].keys()) == expected_fields
        assert response.data[1]['id'] == self.users[0].id
        assert response.data[2]['email'] == self.users[1].email
        assert response.data[3]['full_name'] == f'{self.users[2].first_name} {self.users[2].last_name}'
        assert 'password' not in response.data[1]

    def test_read_list_unauthenticated(self):
        """
        Тест на просмотр списка пользователей анонимным пользователем
        """
        response = self.client.get(self.url)
        assert response.status_code == 401
        assert 'учетные данные не были предоставлены' in str(response.data).lower()

    def test_read_list_not_admin(self):
        self.client.force_authenticate(self.users[0])
        response = self.client.get(self.url)
        assert response.status_code == 403
        assert 'недостаточно прав' in str(response.data)
