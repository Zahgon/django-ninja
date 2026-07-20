from functools import partial
from typing import Any, Callable, Tuple

from typing_extensions import Literal

from ninja.operation import Operation
from ninja.types import TCallable
from ninja.utils import contribute_operation_callback

DecoratorMode = Literal["operation", "view"]



def decorate_view(*decorators: Callable[..., Any]) -> Callable[[TCallable], TCallable]:
    def outer_wrapper(op_func: TCallable) -> TCallable:
        pass

    return outer_wrapper


def _apply_decorators(
    decorators: Tuple[Callable[..., Any]], operation: Operation
) -> None:
    if not hasattr(operation, "_run_decorators"):
        operation._run_decorators = []  # type: ignore
    for deco in decorators:
        operation.run = deco(operation.run)  # type: ignore
        operation._run_decorators.append(deco)  # type: ignore
