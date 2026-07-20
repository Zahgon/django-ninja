from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from django.http import HttpRequest, HttpResponse
from django.urls import URLPattern, URLResolver, reverse
from django.utils.module_loading import import_string

from ninja.constants import NOT_SET, NOT_SET_TYPE
from ninja.decorators import DecoratorMode
from ninja.errors import (
    ConfigError,
    ValidationError,
    ValidationErrorContext,
    set_default_exc_handlers,
)
from ninja.openapi import get_schema
from ninja.openapi.docs import DocsBase, Swagger
from ninja.openapi.schema import OpenAPISchema
from ninja.openapi.urls import get_openapi_urls, get_root_url
from ninja.parser import Parser
from ninja.renderers import BaseRenderer, JSONRenderer
from ninja.router import BoundRouter, Router, RouterMount
from ninja.throttling import BaseThrottle
from ninja.types import DictStrAny, TCallable

if TYPE_CHECKING:
    from .operation import Operation  # pragma: no cover

__all__ = ["NinjaAPI"]

_E = TypeVar("_E", bound=Exception)
Exc = Union[_E, Type[_E]]
ExcHandler = Callable[[HttpRequest, Exc[_E]], HttpResponse]


class NinjaAPI:

    def __init__(
        self,
        *,
        title: str = "NinjaAPI",
        version: str = "1.0.0",
        description: str = "",
        openapi_url: Optional[str] = "/openapi.json",
        docs: DocsBase = Swagger(),
        docs_url: Optional[str] = "/docs",
        docs_decorator: Optional[Callable[[TCallable], TCallable]] = None,
        servers: Optional[List[DictStrAny]] = None,
        urls_namespace: Optional[str] = None,
        auth: Optional[Union[Sequence[Callable], Callable, NOT_SET_TYPE]] = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        renderer: Optional[BaseRenderer] = None,
        parser: Optional[Parser] = None,
        default_router: Optional[Router] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            title: A title for the api.
            description: A description for the api.
            version: The API version.
            urls_namespace: The Django URL namespace for the API. If not provided, the namespace will be ``"api-" + self.version``.
            openapi_url: The relative URL to serve the openAPI spec.
            openapi_extra: Additional attributes for the openAPI spec.
            docs_url: The relative URL to serve the API docs.
            servers: List of target hosts used in openAPI spec.
            auth (Callable | Sequence[Callable] | NOT_SET | None): Authentication class
            renderer: Default response renderer
            parser: Default request parser
        """
        self.title = title
        self.version = version
        self.description = description
        self.openapi_url = openapi_url
        self.docs = docs
        self.docs_url = docs_url
        self.docs_decorator = docs_decorator
        self.servers = servers or []
        self.urls_namespace = urls_namespace or f"api-{self.version}"
        self.renderer = renderer or JSONRenderer()
        self.parser = parser or Parser()
        self.openapi_extra = openapi_extra or {}

        self._exception_handlers: Dict[Exc, ExcHandler] = {}
        self.set_default_exception_handlers()

        self.auth: Optional[Union[Sequence[Callable], NOT_SET_TYPE]]

        if callable(auth):
            self.auth = [auth]
        else:
            self.auth = auth

        self.throttle = throttle

        self._router_registrations: List[
            Tuple[str, Router, Any, Any, Optional[List[str]], Optional[str]]
        ] = []
        self._bound_routers_cache: Optional[List[BoundRouter]] = None

        self._routers: List[Tuple[str, Router]] = []

        self.default_router = default_router or Router()
        self.add_router("", self.default_router)

    def get(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `GET` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.get(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def post(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `POST` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.post(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def delete(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `DELETE` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.delete(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def patch(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `PATCH` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.patch(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def put(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `PUT` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.put(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def api_operation(
        self,
        methods: List[str],
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        return self.default_router.api_operation(
            methods,
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def add_decorator(
        self,
        decorator: Callable,
        mode: DecoratorMode = "operation",
    ) -> None:
        pass

    def add_router(
        self,
        prefix: str,
        router: Union[Router, str],
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        tags: Optional[List[str]] = None,
        url_name_prefix: Optional[str] = None,
        parent_router: Optional[Router] = None,
    ) -> None:
        """
        Add a router to this API.

        Args:
            prefix: URL prefix for all routes in the router
            router: Router instance or import path string
            auth: Authentication override for this router
            throttle: Throttle override for this router
            tags: Tags override for this router
            url_name_prefix: Prefix for URL names (required when mounting same router multiple times)
            parent_router: Internal use - parent router for nested routers
        """
        if self._bound_routers_cache is not None:
            raise ConfigError(
                "Cannot add routers after URLs have been generated. "
                "Add all routers before accessing api.urls"
            )

        if isinstance(router, str):
            router = import_string(router)
            assert isinstance(router, Router)

        existing_templates = {reg[1] for reg in self._router_registrations}
        if router in existing_templates and url_name_prefix is None:
            raise ConfigError(
                "Router is already mounted to this API. When mounting the same router "
                "multiple times, you must provide unique url_name_prefix for each mount."
            )

        self._router_registrations.append((
            prefix,
            router,
            auth,
            throttle,
            tags,
            url_name_prefix,
        ))

        self._routers.append((prefix, router))

    @property
    def urls(self) -> Tuple[List[Union[URLResolver, URLPattern]], str, str]:
        pass

    def _get_bound_routers(self) -> List[BoundRouter]:
        pass

    def _get_urls(self) -> List[Union[URLResolver, URLPattern]]:
        pass

    def get_root_path(self, path_params: DictStrAny) -> str:
        name = f"{self.urls_namespace}:api-root"
        return reverse(name, kwargs=path_params)

    def create_response(
        self,
        request: HttpRequest,
        data: Any,
        *,
        status: Optional[int] = None,
        temporal_response: Optional[HttpResponse] = None,
    ) -> HttpResponse:
        pass

    def create_temporal_response(self, request: HttpRequest) -> HttpResponse:
        pass

    def get_content_type(self) -> str:
        pass

    def get_openapi_schema(
        self,
        *,
        path_prefix: Optional[str] = None,
        path_params: Optional[DictStrAny] = None,
    ) -> OpenAPISchema:
        if path_prefix is None:
            path_prefix = self.get_root_path(path_params or {})
        return get_schema(api=self, path_prefix=path_prefix)

    def get_openapi_operation_id(self, operation: "Operation") -> str:
        pass

    def get_operation_url_name(self, operation: "Operation", router: Router) -> str:
        pass

    def add_exception_handler(
        self, exc_class: Type[_E], handler: ExcHandler[_E]
    ) -> None:
        assert issubclass(exc_class, Exception)
        self._exception_handlers[exc_class] = handler

    def exception_handler(
        self, exc_class: Type[Exception]
    ) -> Callable[[TCallable], TCallable]:
        def decorator(func: TCallable) -> TCallable:
            pass

        return decorator

    def set_default_exception_handlers(self) -> None:
        pass

    def on_exception(self, request: HttpRequest, exc: Exc[_E]) -> HttpResponse:
        pass

    def validation_error_from_error_contexts(
        self, error_contexts: List[ValidationErrorContext]
    ) -> ValidationError:
        pass

    def _lookup_exception_handler(self, exc: Exc[_E]) -> Optional[ExcHandler[_E]]:
        pass

    def _validate(self) -> None:
        pass
