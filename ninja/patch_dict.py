from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
)

from pydantic import BaseModel
from pydantic_core import core_schema

from ninja import Body
from ninja.orm import ModelSchema
from ninja.schema import Schema
from ninja.utils import is_optional_type


class ModelToDict(dict):
    _wrapped_model: Any = None
    _wrapped_model_dump_params: Dict[str, Any] = {}

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: Any, _handler: Any) -> Any:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            cls._wrapped_model.__pydantic_core_schema__,
        )

    @classmethod
    def _validate(cls, input_value: Any) -> Any:
        pass


def get_schema_annotations(schema_cls: Type[Any]) -> Dict[str, Any]:
    pass


def create_patch_schema(schema_cls: Type[Any]) -> Type[ModelToDict]:
    pass


class PatchDictUtil:
    def __getitem__(self, schema_cls: Any) -> Any:
        new_cls = create_patch_schema(schema_cls)
        return Body[new_cls]  # type: ignore


if TYPE_CHECKING:  # pragma: nocover
    T = TypeVar("T")

    class PatchDict(Dict[Any, Any], Generic[T]):
        pass

else:
    PatchDict = PatchDictUtil()
