from rest_framework_simplejwt.tokens import (
    BlacklistedToken,
    OutstandingToken,
    RefreshToken,
    TokenError,
)
from django.db import transaction


def blacklisted_refresh_token(refresh_token):
    token = RefreshToken(refresh_token)
    token.blacklist()


def blacklist_tokens(user):
    with transaction.atomic():
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        blacklisted_tokens = [BlacklistedToken(token=token) for token in outstanding_tokens]
        if blacklisted_tokens:
            BlacklistedToken.objects.bulk_create(blacklisted_tokens)
