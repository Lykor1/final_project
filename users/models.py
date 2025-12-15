from datetime import date
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from teams.models import Team


class UserManager(BaseUserManager):
    def _create_user(self, email, first_name, last_name, password, **extra_fields):
        if not email:
            raise ValueError('Email должен быть обязательно указан')
        if not first_name:
            raise ValueError('Имя пользователя должно быть обязательно указано')
        if not last_name:
            raise ValueError('Фамилия пользователя должна быть обязательно указана')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserWithEmail.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Администратор должен иметь поле is_superuser=True')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Администратор должен иметь поле is_staff=True')
        if extra_fields.get('role') != UserWithEmail.Role.ADMIN:
            raise ValueError('Администратор должен иметь поле role="ADMIN"')
        return self._create_user(email, first_name, last_name, password, **extra_fields)


def _get_age(birthday_date):
    if birthday_date is None:
        return None
    today = date.today()
    age = today.year - birthday_date.year
    if (today.month, today.day) < (birthday_date.month, birthday_date.day):
        age -= 1
    return age


def validate_not_future_date(value):
    if value > date.today():
        raise ValidationError(
            '%(value)s не может быть в будущем',
            params={'value': value}
        )


def validate_minimum_age(value, min_age=18):
    age = _get_age(value)
    if age and age < min_age:
        raise ValidationError(
            f'Минимальный возраст: {min_age} лет. Вам: {age}',
            params={'value': value, 'age': age}
        )


class UserWithEmail(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        USER = 'user', 'пользователь'
        MANAGER = 'manager', 'менеджер'
        ADMIN = 'admin', 'администратор'

    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name="Email")
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    role = models.CharField(max_length=7, choices=Role.choices, default=Role.USER, verbose_name='Роль')
    birthday = models.DateField(blank=True, null=True,
                                validators=(validate_not_future_date, validate_minimum_age),
                                verbose_name='Дата рождения')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True, related_name='members',
                             verbose_name='Команда')
    is_active = models.BooleanField(default=True, verbose_name='Активность')
    is_superuser = models.BooleanField(default=False, verbose_name='Админ')
    is_staff = models.BooleanField(default=False, verbose_name='Доступ к админ-панели')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email', '-created_at']

    def __str__(self):
        return f'{self.email} ({self.last_name} {self.first_name})'

    @property
    def get_age(self):
        return _get_age(self.birthday)
