import itertools
import re
from http.client import responses
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Set, Tuple

from django.utils.termcolors import make_style
from pydantic.json_schema import JsonSchemaMode

from ninja.constants import NOT_SET
from ninja.operation import Operation
from ninja.params.models import TModel, TModels
from ninja.schema import NinjaGenerateJsonSchema
from ninja.types import DictStrAny
from ninja.utils import normalize_path

if TYPE_CHECKING:
    from ninja import NinjaAPI  # pragma: no cover

REF_TEMPLATE: str = "#/components/schemas/{model}"

BODY_CONTENT_TYPES: Dict[str, str] = {
    "body": "application/json",
    "form": "application/x-www-form-urlencoded",
    "file": "multipart/form-data",
}


def get_schema(api: "NinjaAPI", path_prefix: str = "") -> "OpenAPISchema":
    openapi = OpenAPISchema(api, path_prefix)
    return openapi


bold_red_style = make_style(opts=("bold",), fg="red")


class OpenAPISchema(dict):
    def __init__(self, api: "NinjaAPI", path_prefix: str) -> None:
        self.api = api
        self.path_prefix = path_prefix
        self.schemas: DictStrAny = {}
        self.securitySchemes: DictStrAny = {}
        self.all_operation_ids: Set = set()
        extra_info = api.openapi_extra.get("info", {})
        super().__init__([
            ("openapi", "3.1.0"),
            (
                "info",
                {
                    "title": api.title,
                    "version": api.version,
                    "description": api.description,
                    **extra_info,
                },
            ),
            ("paths", self.get_paths()),
            ("components", self.get_components()),
            ("servers", api.servers),
        ])
        for k, v in api.openapi_extra.items():
            if k not in self:
                self[k] = v

    def get_paths(self) -> DictStrAny:
        pass

    def methods(self, operations: list) -> DictStrAny:
        pass

    def deep_dict_update(
        self, main_dict: Dict[Any, Any], update_dict: Dict[Any, Any]
    ) -> None:
        pass

    def operation_details(self, operation: Operation) -> DictStrAny:
        pass

    def operation_parameters(self, operation: Operation) -> List[DictStrAny]:
        pass

    def _extract_parameters(self, model: TModel) -> List[DictStrAny]:
        result = []

        schema = model.model_json_schema(
            ref_template=REF_TEMPLATE,
            schema_generator=NinjaGenerateJsonSchema,
        )

        required = set(schema.get("required", []))
        properties = schema["properties"]

        if "$defs" in schema:
            self.add_schema_definitions(schema["$defs"])

        for name, details in properties.items():
            is_required = name in required
            p_name: str
            p_schema: DictStrAny
            p_required: bool
            for p_name, p_schema, p_required in flatten_properties(
                name, details, is_required, schema.get("$defs", {})
            ):
                if not p_schema.get("include_in_schema", True):
                    continue

                param = {
                    "in": model.__ninja_param_source__,
                    "name": p_name,
                    "schema": p_schema,
                    "required": p_required,
                }

                if "description" in p_schema:
                    param["description"] = p_schema["description"]
                if "examples" in p_schema:
                    param["examples"] = p_schema["examples"]
                elif "example" in p_schema:
                    param["example"] = p_schema["example"]
                if "deprecated" in p_schema:
                    param["deprecated"] = p_schema["deprecated"]

                result.append(param)

        return result

    def _flatten_schema(self, model: TModel) -> DictStrAny:
        params = self._extract_parameters(model)
        flattened = {
            "title": model.__name__,  # type: ignore
            "type": "object",
            "properties": {p["name"]: p["schema"] for p in params},
        }
        required = [p["name"] for p in params if p["required"]]
        if required:
            flattened["required"] = required
        return flattened

    def _create_schema_from_model(
        self,
        model: TModel,
        by_alias: bool = True,
        remove_level: bool = True,
        mode: JsonSchemaMode = "validation",
    ) -> Tuple[DictStrAny, bool]:
        if hasattr(model, "__ninja_flatten_map__"):
            schema = self._flatten_schema(model)
        else:
            schema = model.model_json_schema(
                ref_template=REF_TEMPLATE,
                by_alias=by_alias,
                schema_generator=NinjaGenerateJsonSchema,
                mode=mode,
            ).copy()

        if schema.get("$defs"):
            self.add_schema_definitions(schema.pop("$defs"))

        if remove_level and len(schema["properties"]) == 1:
            name, details = list(schema["properties"].items())[0]

            required = name in schema.get("required", {})
            return details, required
        else:
            return schema, True

    def _create_multipart_schema_from_models(
        self,
        models: TModels,
        mode: JsonSchemaMode = "validation",
    ) -> Tuple[DictStrAny, str]:
        pass

    def request_body(self, operation: Operation) -> DictStrAny:
        pass

    def responses(self, operation: Operation) -> Dict[int, DictStrAny]:
        assert bool(operation.response_models), f"{operation.response_models} empty"

        result = {}
        for status, model in operation.response_models.items():
            if status == Ellipsis:
                continue  # it's not yet clear what it means if user wants to output any other code

            description = responses.get(status, "Unknown Status Code")
            details: Dict[int, Any] = {status: {"description": description}}
            if model not in [None, NOT_SET]:
                schema = self._create_schema_from_model(
                    model, by_alias=operation.by_alias, mode="serialization"
                )[0]
                if operation.stream_format is not None:
                    details[status]["content"] = (
                        operation.stream_format.openapi_content_schema(schema)
                    )
                else:
                    details[status]["content"] = {
                        self.api.renderer.media_type: {"schema": schema}
                    }
            result.update(details)

        return result

    def operation_security(self, operation: Operation) -> Optional[List[DictStrAny]]:
        pass

    def get_components(self) -> DictStrAny:
        pass

    def add_schema_definitions(self, definitions: dict) -> None:
        self.schemas.update(definitions)


def flatten_properties(
    prop_name: str,
    prop_details: DictStrAny,
    prop_required: bool,
    definitions: DictStrAny,
) -> Generator[Tuple[str, DictStrAny, bool], None, None]:
    """
    extracts all nested model's properties into flat properties
    (used f.e. in GET params with multiple arguments and models)
    """
    if "allOf" in prop_details:
        resolve_allOf(prop_details, definitions)
        if len(prop_details["allOf"]) == 1 and "enum" in prop_details["allOf"][0]:
            yield prop_name, prop_details, prop_required
        else:  # pragma: no cover
            for item in prop_details["allOf"]:
                yield from flatten_properties("", item, True, definitions)

    elif "items" in prop_details and "$ref" in prop_details["items"]:
        def_name = prop_details["items"]["$ref"].rsplit("/", 1)[-1]
        prop_details["items"].update(definitions[def_name])
        del prop_details["items"]["$ref"]  # seems num data is there so ref not needed
        yield prop_name, prop_details, prop_required

    elif "$ref" in prop_details:
        def_name = prop_details["$ref"].split("/")[-1]
        definition = definitions[def_name]
        yield from flatten_properties(prop_name, definition, prop_required, definitions)

    elif "properties" in prop_details:
        required = set(prop_details.get("required", []))
        for k, v in prop_details["properties"].items():
            is_required = k in required
            yield from flatten_properties(k, v, is_required, definitions)
    else:
        yield prop_name, prop_details, prop_required


def resolve_allOf(details: DictStrAny, definitions: DictStrAny) -> None:
    """
    resolves all $ref's in 'allOf' section
    """
    for item in details["allOf"]:
        if "$ref" in item:
            def_name = item["$ref"].rsplit("/", 1)[-1]
            item.update(definitions[def_name])
            del item["$ref"]


def merge_schemas(schemas: List[DictStrAny]) -> DictStrAny:
    pass
