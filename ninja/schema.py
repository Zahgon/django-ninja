
import warnings
from typing import (
    Any,
    Callable,
    Dict,
    Type,
    TypeVar,
    Union,
    no_type_check,
)

import pydantic
from django.db.models import Manager, QuerySet
from django.db.models.fields.files import FieldFile
from django.template import Variable, VariableDoesNotExist
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator
from pydantic._internal._model_construction import ModelMetaclass
from pydantic.functional_validators import ModelWrapValidatorHandler
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from typing_extensions import dataclass_transform

from ninja.signature.utils import get_args_names, has_kwargs
from ninja.types import DictStrAny

pydantic_version = list(map(int, pydantic.VERSION.split(".")[:2]))
assert pydantic_version >= [2, 0], "Pydantic 2.0+ required"

__all__ = ["BaseModel", "Field", "DjangoGetter", "Schema"]

S = TypeVar("S", bound="Schema")


class DjangoGetter:
    __slots__ = ("_obj", "_schema_cls", "_context", "__dict__")

    def __init__(self, obj: Any, schema_cls: Type[S], context: Any = None):
        self._obj = obj
        self._schema_cls = schema_cls
        self._context = context

    def __getattr__(self, key: str) -> Any:

        resolver = self._schema_cls._ninja_resolvers.get(key)
        if resolver:
            value = resolver(getter=self)
        else:
            if isinstance(self._obj, dict):
                if key not in self._obj:
                    raise AttributeError(key)
                value = self._obj[key]
            else:
                try:
                    value = getattr(self._obj, key)
                except AttributeError:
                    try:
                        value = Variable(key).resolve(self._obj)
                    except VariableDoesNotExist as e:
                        raise AttributeError(key) from e
        return self._convert_result(value)


    def _convert_result(self, result: Any) -> Any:
        pass

    def __repr__(self) -> str:
        return f"<DjangoGetter: {repr(self._obj)}>"


class Resolver:
    __slots__ = ("_func", "_static", "_takes_context")
    _static: bool
    _func: Any
    _takes_context: bool

    def __init__(self, func: Union[Callable, staticmethod]):
        if isinstance(func, staticmethod):
            self._static = True
            self._func = func.__func__
        else:
            self._static = False
            self._func = func

        arg_names = get_args_names(self._func)
        self._takes_context = has_kwargs(self._func) or "context" in arg_names

    def __call__(self, getter: DjangoGetter) -> Any:
        kwargs = {}
        if self._takes_context:
            kwargs["context"] = getter._context

        if self._static:
            return self._func(getter._obj, **kwargs)
        raise NotImplementedError(
            "Non static resolves are not supported yet"
        )  # pragma: no cover





@dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class ResolverMetaclass(ModelMetaclass):
    _ninja_resolvers: Dict[str, Resolver]

    @no_type_check
    def __new__(cls, name, bases, namespace, **kwargs):
        resolvers = {}

        for base in reversed(bases):
            base_resolvers = getattr(base, "_ninja_resolvers", None)
            if base_resolvers:
                resolvers.update(base_resolvers)
        for attr, resolve_func in namespace.items():
            if not attr.startswith("resolve_"):
                continue
            if (
                not callable(resolve_func)
                and not isinstance(resolve_func, staticmethod)
            ):
                continue  # pragma: no cover
            resolvers[attr[8:]] = Resolver(resolve_func)

        result = super().__new__(cls, name, bases, namespace, **kwargs)
        result._ninja_resolvers = resolvers
        return result


class NinjaGenerateJsonSchema(GenerateJsonSchema):
    def default_schema(self, schema: Any) -> JsonSchemaValue:
        pass


class Schema(BaseModel, metaclass=ResolverMetaclass):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="wrap")
    @classmethod
    def _run_root_validator(
        cls, values: Any, handler: ModelWrapValidatorHandler[S], info: ValidationInfo
    ) -> Any:
        pass

    @classmethod
    def from_orm(cls: Type[S], obj: Any, **kw: Any) -> S:
        pass

    def dict(self, *a: Any, **kw: Any) -> DictStrAny:
        pass

    @classmethod
    def json_schema(cls) -> DictStrAny:
        pass

    @classmethod
    def schema(cls) -> DictStrAny:  # type: ignore
        pass
