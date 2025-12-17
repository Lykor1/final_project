import pytest
from datetime import datetime, timezone
from rest_framework_simplejwt.tokens import (
    RefreshToken,
    BlacklistedToken,
    TokenError,
    OutstandingToken
)

from users.services import blacklisted_refresh_token, blacklist_tokens


@pytest.mark.services
@pytest.mark.django_db
class TestBlacklistedRefreshToken:
    @pytest.fixture(autouse=True)
    def setup(self, user_data, create_user):
        user_data.pop('password2')
        self.refresh = RefreshToken.for_user(create_user(**user_data))

    def test_blacklisted_refresh_token_success(self):
        """
        Тест на успешное добавление токена в blacklist
        """
        blacklisted_refresh_token(str(self.refresh))
        assert BlacklistedToken.objects.filter(token__jti=self.refresh['jti']).exists()

    def test_blacklisted_refresh_token_idempotent(self):
        """
        Тест на повторное добавление токена в blacklist
        """
        blacklisted_refresh_token(str(self.refresh))
        with pytest.raises(TokenError):
            blacklisted_refresh_token(str(self.refresh))
        assert BlacklistedToken.objects.filter(token__jti=self.refresh['jti']).count() == 1

    def test_blacklisted_refresh_invalid_token(self):
        """
        Тест на добавление недействительного токена в blacklist
        """
        with pytest.raises(TokenError):
            blacklisted_refresh_token('invalid.token.value')


@pytest.mark.services
@pytest.mark.django_db
class TestBlacklistToken:
    @pytest.fixture(autouse=True)
    def setup(self, user_data, create_user):
        user_data.pop('password2')
        self.user = create_user(**user_data)
        user_data.update({'email': 'another@example.com'})
        self.another_user = create_user(**user_data)

    def create_n_tokens(self, user, n):
        for _ in range(n):
            RefreshToken.for_user(user)

    def test_blacklist_tokens_success(self):
        """
        Тест на успешное занесение токенов в blacklist
        """
        self.create_n_tokens(self.user, 3)
        assert OutstandingToken.objects.filter(user=self.user).count() == 3
        assert BlacklistedToken.objects.filter(token__user=self.user).count() == 0
        blacklist_tokens(self.user)
        assert BlacklistedToken.objects.filter(token__user=self.user).count() == 3
        outstanding_pks = set(OutstandingToken.objects.filter(user=self.user).values_list('pk', flat=True))
        blacklisted_pks = set(BlacklistedToken.objects.filter(token__user=self.user).values_list('token_id', flat=True))
        assert outstanding_pks == blacklisted_pks

    def test_blacklist_tokens_current_user(self):
        """
        Тест на занесение токенов с blacklist только у указанного пользователя
        """
        self.create_n_tokens(self.user, 2)
        self.create_n_tokens(self.another_user, 3)
        assert OutstandingToken.objects.filter(user=self.user).count() == 2
        assert OutstandingToken.objects.filter(user=self.another_user).count() == 3
        blacklist_tokens(self.user)
        assert BlacklistedToken.objects.filter(token__user=self.user).count() == 2
        assert BlacklistedToken.objects.filter(token__user=self.another_user).count() == 0

    def test_blacklist_tokens_idempotent(self):
        """
        Тест на повторное занесение токенов с blacklist
        """
        self.create_n_tokens(self.user, 2)
        blacklist_tokens(self.user)
        count_first = BlacklistedToken.objects.filter(token__user=self.user).count()
        assert count_first == 2
        blacklist_tokens(self.user)
        count_second = BlacklistedToken.objects.filter(token__user=self.user).count()
        assert count_second == count_first

    def test_blacklist_no_tokens_does_nothing(self):
        """
        Тест на отсутствие токенов у пользователя
        """
        assert OutstandingToken.objects.filter(user=self.user).count() == 0
        blacklist_tokens(self.user)
        assert BlacklistedToken.objects.filter(token__user=self.user).count() == 0
