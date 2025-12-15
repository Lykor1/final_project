import pytest
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.models
@pytest.mark.django_db
class TestUserModel:
    @pytest.fixture(autouse=True)
    def setup(self, user_data):
        user_data.pop('password2')
        return user_data

    def test_create_user_success(self, create_user, user_data):
        """
        Тест на успешное создание записи
        """
        created_user = create_user(**user_data)
        assert created_user.pk is not None
        assert created_user.email == user_data['email']
        assert created_user.check_password(user_data['password'])
        assert created_user.is_active is True
        assert created_user.is_superuser is False
        assert created_user.is_staff is False
        assert created_user.role == User.Role.USER

    @pytest.mark.parametrize(
        'field',
        [
            'email',
            'first_name',
            'last_name'
        ]
    )
    def test_create_user_without_required_fields(self, create_user, user_data, field):
        """
        Тест на создание без обязательного поля
        """
        data = user_data.copy()
        data[field] = None
        with pytest.raises(ValueError):
            create_user(**data)

    def test_unique_email(self, user, create_user, user_data):
        """
        Тест на уникальность email
        """
        with pytest.raises(IntegrityError):
            create_user(**user_data)

    def test_create_superuser_success(self, admin_user):
        """
        Тест на успешное создание админа
        """
        assert admin_user.is_superuser is True
        assert admin_user.is_staff is True
        assert admin_user.role == User.Role.ADMIN

    @pytest.mark.parametrize(
        'flags',
        [
            {'is_staff': False},
            {'is_superuser': False},
            {'role': None}
        ]
    )
    def test_create_superuser_with_wrong_flags(self, admin_user, flags):
        """
        Тест на создание админа с невалидными флагами/ролью
        """
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email='badadmin@example.com',
                first_name='bad',
                last_name='admin',
                password='badadmin123',
                **flags
            )

    def test_birthday_in_future(self, user_data, future_birthday):
        """
        Тест на дату рождения в будущем
        """
        created_user = User(**user_data)
        created_user.birthday = future_birthday
        with pytest.raises(ValidationError):
            created_user.full_clean()

    def test_underage_user(self, user_data, minor_birthday):
        """
        Тест на несовершеннолетнего пользователя
        """
        created_user = User(**user_data)
        created_user.birthday = minor_birthday
        with pytest.raises(ValidationError):
            created_user.full_clean()

    def test_birthday_can_be_null(self, user_data):
        """
        Тест на отсутствие даты рождения
        """
        created_user = User(**user_data)
        created_user.birthday = None
        created_user.full_clean()

    def test_get_age_returns_correct_value(self, user, adult_birthday):
        """
        Тест на корректный возврат возраста
        """
        expected_age = date.today().year - adult_birthday.year
        assert user.get_age == expected_age

    def test_get_age_returns_none(self, user):
        """
        Тест на отсутствие возраста при отсутствии даты рождения
        """
        user.birthday = None
        assert user.get_age is None

    def test_user_can_have_team(self, user, team):
        """
        Тест на team у пользователя
        """
        user.team = team
        user.save()
        assert user.team == team
        assert user in team.members.all()

    def test_str_representation(self, user):
        """
        Тест на __str__
        """
        assert str(user) == f'{user.email} ({user.last_name} {user.first_name})'

    def test_default_ordering(self):
        """
        Тест на сортировку
        """
        fields = User._meta.ordering
        assert fields == ['email', '-created_at']
