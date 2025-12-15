import pytest
from django.contrib.auth import get_user_model

from users.serializers import UserRegisterSerializer

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
