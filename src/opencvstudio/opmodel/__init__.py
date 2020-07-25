from abc import ABC
from dataclasses import dataclass
from typing import Callable, Iterable, List, Type, Union

from opencvstudio.primitives.image import Image, ImageSpec


class OperationContext:

    def __init__(self):
        pass


class OperationResult:
    def __init__(self, image: Image):
        self.image = image


Errors = Iterable[Union[str, Exception, Warning]]


class Operation(ABC):
    """
    Extension point for operations
    """

    def execute(self, ctx: OperationContext, image: Image) -> Image:
        pass

    def errors(self, img: ImageSpec) -> Errors:
        return []


@dataclass
class Parameter:
    name: str
    ty: Type
    default: Union[Callable[[Image], object], object]


class Module:

    def __init__(self, name: str, operations: List[Operation],
                 parameters: List[Parameter]):
        self.name = name
        self.operations = operations
        self.parameters = parameters
