import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

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
