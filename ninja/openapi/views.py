from typing import TYPE_CHECKING, Any, NoReturn

from django.http import Http404, HttpRequest, HttpResponse

from ninja.openapi.docs import DocsBase
from ninja.responses import Response

if TYPE_CHECKING:
    from ninja import NinjaAPI  # pragma: no cover


def default_home(request: HttpRequest, api: "NinjaAPI", **kwargs: Any) -> NoReturn:
    pass


def openapi_json(request: HttpRequest, api: "NinjaAPI", **kwargs: Any) -> HttpResponse:
    pass


def openapi_view(request: HttpRequest, api: "NinjaAPI", **kwargs: Any) -> HttpResponse:
    pass
