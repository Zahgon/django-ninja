from typing import Any, List, Optional, Union, no_type_check

from django.apps import apps
from django.db.models import Model as DjangoModel
from pydantic.dataclasses import dataclass

from ninja.compatibility.util import get_annotations_from_namespace
from ninja.errors import ConfigError
from ninja.orm.factory import create_schema
from ninja.schema import ResolverMetaclass, Schema

_is_modelschema_class_defined = False


@dataclass
class MetaConf:
    model: Any
    fields: Optional[List[str]] = None
    exclude: Union[List[str], str, None] = None
    fields_optional: Union[List[str], str, None] = None

    @staticmethod
    def from_schema_class(name: str, namespace: dict) -> "MetaConf":
        pass


class ModelSchemaMetaclass(ResolverMetaclass):
    @no_type_check
    def __new__(
        mcs,
        name: str,
        bases: tuple,
        namespace: dict,
        **kwargs,
    ):
        cls = super().__new__(
            mcs,
            name,
            bases,
            namespace,
            **kwargs,
        )
        for base in reversed(bases):
            if (
                _is_modelschema_class_defined
                and issubclass(base, ModelSchema)
                and base == ModelSchema
            ):
                meta_conf = MetaConf.from_schema_class(name, namespace)

                custom_fields = []
                annotations = get_annotations_from_namespace(namespace)
                for attr_name, type in annotations.items():
                    if attr_name.startswith("_"):
                        continue
                    default = namespace.get(attr_name, ...)
                    custom_fields.append((attr_name, type, default))



                model_schema = create_schema(
                    meta_conf.model,
                    name=name,
                    fields=meta_conf.fields,
                    exclude=meta_conf.exclude,
                    optional_fields=meta_conf.fields_optional,
                    custom_fields=custom_fields,
                    base_class=cls,
                )
                model_schema.__doc__ = cls.__doc__
                return model_schema

        return cls


class ModelSchema(Schema, metaclass=ModelSchemaMetaclass):
    pass


_is_modelschema_class_defined = True
