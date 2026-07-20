from typing import Any, Optional

from django.conf import settings
from django.http import HttpRequest

from ninja.security.apikey import APIKeyCookie

__all__ = ["SessionAuth", "SessionAuthSuperUser", "SessionAuthIsStaff"]


class SessionAuth(APIKeyCookie):

    param_name: str = settings.SESSION_COOKIE_NAME

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        pass


class SessionAuthSuperUser(APIKeyCookie):

    param_name: str = settings.SESSION_COOKIE_NAME

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        pass


class SessionAuthIsStaff(SessionAuthSuperUser):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        pass
