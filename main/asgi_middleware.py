from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    if not token:
        return AnonymousUser()
    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        return User.objects.get(id=user_id)
    except (TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


def _parse_token_from_scope(scope):
    """Extract the JWT token from the query string."""
    qs = scope.get("query_string", b"").decode()
    params = parse_qs(qs)
    return params.get("token", [None])[0]


class OptionalJWTAuthMiddleware:
    """
    Channels middleware that OPTIONALLY parses a JWT token.
    Always allows the connection, even for anonymous users.
    Use for routes where anyone can connect and read, but sending
    messages may require authentication (checked in the consumer).
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = _parse_token_from_scope(scope)
        scope["user"] = await get_user_from_token(token)

        # Always allow the connection, regardless of auth status
        return await self.app(scope, receive, send)
