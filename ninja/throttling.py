import hashlib
import time
from typing import Dict, List, Optional, Tuple

from django.core.cache import cache as default_cache
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest


class BaseThrottle:

    def allow_request(self, request: HttpRequest) -> bool:
        """
        Return `True` if the request should be allowed, `False` otherwise.
        """
        raise NotImplementedError(".allow_request() must be overridden")

    def get_ident(self, request: HttpRequest) -> Optional[str]:
        pass

    def wait(self) -> Optional[float]:
        pass


class SimpleRateThrottle(BaseThrottle):

    from ninja.conf import settings

    cache = default_cache
    timer = time.time
    cache_format = "throttle_%(scope)s_%(ident)s"
    scope: Optional[str] = None
    THROTTLE_RATES: Dict[str, Optional[str]] = settings.DEFAULT_THROTTLE_RATES
    _PERIODS = {
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24,
        "sec": 1,
        "min": 60,
        "hour": 60 * 60,
        "day": 60 * 60 * 24,
    }

    def __init__(self, rate: Optional[str] = None):
        self.rate: Optional[str]
        if rate:
            self.rate = rate
        else:
            self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def get_cache_key(self, request: HttpRequest) -> Optional[str]:
        """
        Should return a unique cache-key which can be used for throttling.
        Must be overridden.

        May return `None` if the request should not be throttled.
        """
        raise NotImplementedError(".get_cache_key() must be overridden")

    def get_rate(self) -> Optional[str]:
        pass

    def parse_rate(self, rate: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        pass

    def allow_request(self, request: HttpRequest) -> bool:
        pass

    def throttle_success(self) -> bool:
        pass

    def throttle_failure(self) -> bool:
        pass

    def wait(self) -> Optional[float]:
        pass


class AnonRateThrottle(SimpleRateThrottle):

    scope = "anon"

    def get_cache_key(self, request: HttpRequest) -> Optional[str]:
        pass


class AuthRateThrottle(SimpleRateThrottle):

    scope = "auth"

    def get_cache_key(self, request: HttpRequest) -> str:
        pass


class UserRateThrottle(SimpleRateThrottle):

    scope = "user"

    def get_cache_key(self, request: HttpRequest) -> str:
        pass
