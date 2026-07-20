import warnings
from typing import Any, List, Optional, TypeVar, Union, cast

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, QuerySet
from pydantic import ConfigDict
from pydantic.fields import FieldInfo
from typing_extensions import Literal

from .constants import NOT_SET
from .schema import Schema

ExpressionConnector = Literal["AND", "OR", "XOR"]

DEFAULT_IGNORE_NONE: bool = True
DEFAULT_CLASS_LEVEL_EXPRESSION_CONNECTOR: ExpressionConnector = "AND"
DEFAULT_FIELD_LEVEL_EXPRESSION_CONNECTOR: ExpressionConnector = "OR"


class FilterLookup:

    def __init__(
        self,
        q: Union[str, List[str], None],
        *,
        expression_connector: ExpressionConnector = DEFAULT_FIELD_LEVEL_EXPRESSION_CONNECTOR,
        ignore_none: bool = DEFAULT_IGNORE_NONE,
    ):
        """
        Args:
            q: Database lookup expression(s). Can be:
                - A string like "name__icontains"
                - A list of strings like ["name__icontains", "email__icontains"]
                - Use "__" prefix for implicit field name: "__icontains" becomes "fieldname__icontains"
            expression_connector: How to combine multiple field-level expressions ("OR", "AND", "XOR"). Default is "OR".
            ignore_none: Whether to ignore None values for this field specifically. Default is True.
        """
        self.q = q
        self.expression_connector = expression_connector
        self.ignore_none = ignore_none


T = TypeVar("T", bound=QuerySet)


class FilterConfigDict(ConfigDict, total=False):
    ignore_none: bool
    expression_connector: ExpressionConnector


class FilterSchema(Schema):
    model_config = FilterConfigDict(
        ignore_none=DEFAULT_IGNORE_NONE,
        expression_connector=DEFAULT_CLASS_LEVEL_EXPRESSION_CONNECTOR,
    )

    def custom_expression(self) -> Q:
        """
        Implement this method to return a combination of filters that will be used
        """
        raise NotImplementedError

    def get_filter_expression(self) -> Q:
        pass

    def filter(self, queryset: T) -> T:
        pass

    def _get_filter_lookup(
        self, field_name: str, field_info: FieldInfo
    ) -> Optional[FilterLookup]:
        pass

    def _get_field_q_expression(
        self,
        field_name: str,
        field_info: FieldInfo,
    ) -> Union[str, List[str], None]:
        pass

    def _get_field_expression_connector(
        self,
        field_name: str,
        field_info: FieldInfo,
    ) -> Union[ExpressionConnector, None]:
        pass

    def _get_field_ignore_none(
        self, field_name: str, field_info: FieldInfo
    ) -> Union[bool, None]:
        pass

    def _resolve_field_expression(
        self, field_name: str, field_value: Any, field_info: FieldInfo
    ) -> Q:
        pass

    def _connect_fields(self) -> Q:
        pass

    def _get_from_deprecated_field_extra(
        self, field_name: str, field_info: FieldInfo, attr: str
    ) -> Union[Any, None]:
        pass
