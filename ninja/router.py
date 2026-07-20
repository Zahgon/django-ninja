import re
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

from django.urls import URLPattern
from django.urls import path as django_path
from django.utils.module_loading import import_string

from ninja.constants import NOT_SET, NOT_SET_TYPE
from ninja.decorators import DecoratorMode
from ninja.errors import ConfigError
from ninja.operation import PathView
from ninja.throttling import BaseThrottle
from ninja.types import TCallable
from ninja.utils import normalize_path, replace_path_param_notation

if TYPE_CHECKING:
    from ninja import NinjaAPI  # pragma: no cover


__all__ = ["Router", "RouterMount", "BoundRouter"]


@dataclass
class RouterMount:

    template: "Router"
    prefix: str
    url_name_prefix: Optional[str] = None
    auth: Any = NOT_SET
    throttle: Any = NOT_SET
    tags: Optional[List[str]] = None
    inherited_decorators: List[Tuple[Callable, DecoratorMode]] = field(
        default_factory=list
    )
    inherited_auth: Any = NOT_SET
    inherited_throttle: Any = NOT_SET
    inherited_tags: Optional[List[str]] = None


class BoundRouter:

    def __init__(self, mount: RouterMount, api: "NinjaAPI") -> None:
        self.mount = mount
        self.template = mount.template
        self.api = api
        self.prefix = mount.prefix
        self.url_name_prefix = mount.url_name_prefix

        if mount.auth is not NOT_SET:
            self.auth = mount.auth
        elif mount.template.auth is not NOT_SET:
            self.auth = mount.template.auth
        elif mount.inherited_auth is not NOT_SET:
            self.auth = mount.inherited_auth
        else:
            self.auth = NOT_SET

        if mount.throttle is not NOT_SET:
            self.throttle = mount.throttle
        elif mount.template.throttle is not NOT_SET:
            self.throttle = mount.template.throttle
        elif mount.inherited_throttle is not NOT_SET:
            self.throttle = mount.inherited_throttle
        else:
            self.throttle = NOT_SET

        self.tags: Optional[List[str]]
        if mount.tags is not None:
            self.tags = mount.tags
        else:
            accumulated_tags: List[str] = []
            if mount.inherited_tags is not None:
                accumulated_tags.extend(mount.inherited_tags)
            if mount.template.tags is not None:
                accumulated_tags.extend(mount.template.tags)
            self.tags = accumulated_tags or None

        self.path_operations: Dict[str, PathView] = {}
        self._bind_operations()

    def _bind_operations(self) -> None:
        pass

    def urls_paths(self, prefix: str) -> Iterator[URLPattern]:
        pass


class Router:
    def __init__(
        self,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        tags: Optional[List[str]] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
    ) -> None:
        self._frozen = False
        self.auth = auth
        self.throttle = throttle
        self.tags = tags
        self.by_alias = by_alias
        self.exclude_unset = exclude_unset
        self.exclude_defaults = exclude_defaults
        self.exclude_none = exclude_none

        self.path_operations: Dict[str, PathView] = {}
        self._routers: List[Tuple[str, Router, Optional[List[str]]]] = []
        self._decorators: List[Tuple[Callable, DecoratorMode]] = []

    def _freeze(self) -> None:
        pass

    def _check_not_frozen(self) -> None:
        """Raise error if attempting to modify a frozen router."""
        if self._frozen:
            raise ConfigError(
                "Cannot modify router after URLs have been generated. "
                "Routers become frozen when api.urls is accessed."
            )

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
        return self.api_operation(
            ["GET"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["POST"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["DELETE"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["PATCH"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["PUT"],
            path,
            auth=auth,
            throttle=throttle,
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
        def decorator(view_func: TCallable) -> TCallable:
            pass

        return decorator

    def add_api_operation(
        self,
        path: str,
        methods: List[str],
        view_func: Callable,
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
    ) -> None:
        self._check_not_frozen()
        path = re.sub(r"\{uuid:(\w+)\}", r"{uuidstr:\1}", path, flags=re.IGNORECASE)


        if path not in self.path_operations:
            path_view = PathView()
            self.path_operations[path] = path_view
        else:
            path_view = self.path_operations[path]

        by_alias = by_alias is None and self.by_alias or by_alias
        exclude_unset = exclude_unset is None and self.exclude_unset or exclude_unset
        exclude_defaults = (
            exclude_defaults is None and self.exclude_defaults or exclude_defaults
        )
        exclude_none = exclude_none is None and self.exclude_none or exclude_none

        path_view.add_operation(
            path=path,
            methods=methods,
            view_func=view_func,
            auth=auth,
            throttle=throttle,
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

        return None

    def urls_paths(
        self, prefix: str, api: Optional["NinjaAPI"] = None
    ) -> Iterator[URLPattern]:
        pass

    def add_router(
        self,
        prefix: str,
        router: Union["Router", str],
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        tags: Optional[List[str]] = None,
    ) -> None:
        self._check_not_frozen()

        if isinstance(router, str):
            router = import_string(router)
            assert isinstance(router, Router)

        if auth != NOT_SET:
            router.auth = auth
        if throttle != NOT_SET:
            router.throttle = throttle
        self._routers.append((prefix, router, tags))

    def add_decorator(
        self,
        decorator: Callable,
        mode: DecoratorMode = "operation",
    ) -> None:
        pass

    def build_routers(
        self,
        prefix: str,
        inherited_decorators: Optional[List[Tuple[Callable, DecoratorMode]]] = None,
        inherited_auth: Any = NOT_SET,
        inherited_throttle: Any = NOT_SET,
        inherited_tags: Optional[List[str]] = None,
    ) -> List[RouterMount]:
        pass

    def _apply_decorators_to_operations(self) -> None:
        pass
