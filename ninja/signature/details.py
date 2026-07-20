import inspect
import warnings
from collections import defaultdict, namedtuple
from sys import version_info
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple

import pydantic
from django.http import HttpResponse
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated, get_args, get_origin

from ninja import UploadedFile
from ninja.compatibility.util import UNION_TYPES
from ninja.errors import ConfigError
from ninja.params.models import (
    Body,
    File,
    Form,
    Param,
    Path,
    Query,
    TModel,
    TModels,
    _MultiPartBody,
)
from ninja.signature.utils import get_path_param_names, get_typed_signature
from ninja.utils import is_optional_type

__all__ = [
    "ViewSignature",
    "is_pydantic_model",
    "is_collection_type",
    "detect_collection_fields",
]

FuncParam = namedtuple(
    "FuncParam", ["name", "alias", "source", "annotation", "is_collection"]
)


class ViewSignature:
    FLATTEN_PATH_SEP = (
        "\x1e"  # ASCII Record Separator.  IE: not generally used in query names
    )
    response_arg: Optional[str] = None

    def __init__(self, path: str, view_func: Callable[..., Any]) -> None:
        self.view_func = view_func
        self.signature = get_typed_signature(self.view_func)
        self.path = path
        self.path_params_names = get_path_param_names(path)
        self.docstring = inspect.cleandoc(view_func.__doc__ or "")
        self.has_kwargs = False

        self.params = []
        for name, arg in self.signature.parameters.items():
            if name == "request":
                continue

            if arg.kind == arg.VAR_KEYWORD:
                self.has_kwargs = True
                continue

            if arg.kind == arg.VAR_POSITIONAL:
                continue

            if arg.annotation is HttpResponse:
                self.response_arg = name
                continue

            if (
                arg.annotation is inspect.Parameter.empty
                and isinstance(arg.default, type)
                and issubclass(arg.default, pydantic.BaseModel)
            ):
                raise ConfigError(
                    f"Looks like you are using `{name}={arg.default.__name__}` instead of `{name}: {arg.default.__name__}` (annotation)"
                )

            func_param = self._get_param_type(name, arg)
            self.params.append(func_param)

        if hasattr(view_func, "_ninja_contribute_args"):
            for p_name, p_type, p_source in view_func._ninja_contribute_args:
                self.params.append(
                    FuncParam(p_name, p_source.alias or p_name, p_source, p_type, False)
                )

        self.models: TModels = self._create_models()

        self._validate_view_path_params()

    def _validate_view_path_params(self) -> None:
        pass

    def _create_models(self) -> TModels:
        pass

    def _args_flatten_map(self, args: List[FuncParam]) -> Dict[str, Tuple[str, ...]]:
        pass

    def _model_flatten_map(self, model: TModel, prefix: str) -> Generator:
        pass

    def _get_param_type(self, name: str, arg: inspect.Parameter) -> FuncParam:
        pass


def _unwrap_union_model(annotation: Any) -> Any:
    pass


def is_pydantic_model(cls: Any) -> bool:
    try:
        origin = get_origin(cls)

        if origin is Annotated:
            args = get_args(cls)
            return is_pydantic_model(args[0])

        if origin in UNION_TYPES:
            return any(issubclass(arg, pydantic.BaseModel) for arg in get_args(cls))
        return issubclass(cls, pydantic.BaseModel)
    except TypeError:  # pragma: no cover
        return False


def is_collection_type(annotation: Any) -> bool:
    origin = get_origin(annotation)

    if origin in UNION_TYPES:
        for arg in get_args(annotation):
            if is_collection_type(arg):
                return True
        return False

    collection_types = (List, list, set, tuple)
    if origin is None:
        return (
            isinstance(annotation, collection_types)
            if not isinstance(annotation, type)
            else issubclass(annotation, collection_types)
        )
    else:
        return origin in collection_types  # TODO: I guess we should handle only list


def detect_collection_fields(
    args: List[FuncParam], flatten_map: Dict[str, Tuple[str, ...]]
) -> List[str]:
    pass
