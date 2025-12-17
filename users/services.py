from rest_framework_simplejwt.tokens import (
    BlacklistedToken,
    OutstandingToken,
    RefreshToken,
    TokenError,
)


def blacklist_token(user):
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)
