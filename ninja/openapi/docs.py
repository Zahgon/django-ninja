import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from ninja.constants import NOT_SET
from ninja.types import DictStrAny

if TYPE_CHECKING:
    from ninja import NinjaAPI  # pragma: no cover

ABS_TPL_PATH = Path(__file__).parent.parent / "templates/ninja/"


class DocsBase(ABC):
    @abstractmethod
    def render_page(
        self, request: HttpRequest, api: "NinjaAPI", **kwargs: Any
    ) -> HttpResponse:
        pass  # pragma: no cover

    def get_openapi_url(self, api: "NinjaAPI", path_params: DictStrAny) -> str:
        pass


class Swagger(DocsBase):
    template = "ninja/swagger.html"
    template_cdn = str(ABS_TPL_PATH / "swagger_cdn.html")
    default_settings = {
        "layout": "BaseLayout",
        "deepLinking": True,
    }

    def __init__(self, settings: Optional[DictStrAny] = None):
        self.settings = {}
        self.settings.update(self.default_settings)
        if settings:
            self.settings.update(settings)

    def render_page(
        self, request: HttpRequest, api: "NinjaAPI", **kwargs: Any
    ) -> HttpResponse:
        pass


class Redoc(DocsBase):
    template = "ninja/redoc.html"
    template_cdn = str(ABS_TPL_PATH / "redoc_cdn.html")
    default_settings: DictStrAny = {}

    def __init__(self, settings: Optional[DictStrAny] = None):
        self.settings = {}
        self.settings.update(self.default_settings)
        if settings:
            self.settings.update(settings)

    def render_page(
        self, request: HttpRequest, api: "NinjaAPI", **kwargs: Any
    ) -> HttpResponse:
        pass


def render_template(
    request: HttpRequest, template: str, template_cdn: str, context: DictStrAny
) -> HttpResponse:
    pass


def _render_cdn_template(
    request: HttpRequest, template_path: str, context: Optional[DictStrAny] = None
) -> HttpResponse:
    pass


def _csrf_needed(api: "NinjaAPI") -> bool:
    pass
