from dataclasses import dataclass
from typing import Iterable, Union

from opencvstudio.opmodel import Errors, Operation, OperationContext, Parameter
from opencvstudio.primitives.color import ColorSpace
from opencvstudio.dataops import can_convert_color, convert_color
from opencvstudio.primitives.image import Image, ImageSpec


@dataclass
class ChangeColorSpaceOp(Operation):

    target: ColorSpace = ColorSpace.GRAY

    @classmethod
    def parameters(cls):
        return [
            Parameter("target", ColorSpace, ColorSpace.GRAY)
        ]

    def __init__(self, target: ColorSpace):
        self.target = target

    def execute(self, ctx: OperationContext, img: Image) -> Image:
        return img.replace_color_data(
            convert_color(img.data, img.color, self.target),
            self.target)

    def errors(self, img: ImageSpec) -> Errors:
        if not can_convert_color(img.color, self.target):
            return (f"Can not convert from {img.color} to {self.target}"
                    f" color space",)

        return ()
