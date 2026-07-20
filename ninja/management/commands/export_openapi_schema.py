import json
from pathlib import Path
from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.urls.base import resolve
from django.utils.module_loading import import_string

from ninja.main import NinjaAPI
from ninja.management.utils import command_docstring
from ninja.responses import NinjaJSONEncoder


class Command(BaseCommand):

    help = "Exports Open API schema"

    def _get_api_instance(self, api_path: Optional[str] = None) -> NinjaAPI:
        pass

    def add_arguments(self, parser: CommandParser) -> None:
        pass

    def handle(self, *args: Any, **options: Any) -> None:
        pass


__doc__ = command_docstring(Command)
