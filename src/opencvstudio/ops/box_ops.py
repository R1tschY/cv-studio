from dataclasses import dataclass

from opencvstudio.dataops import crop
from opencvstudio.opmodel import Operation, OperationContext, Parameter
from opencvstudio.primitives.image import Image
from opencvstudio.primitives import Box


@dataclass
class CropOp(Operation):

    box: Box

    @classmethod
    def parameters(cls):
        return [
            Parameter("box", Box, lambda img: Box.from_size(img.size))
        ]

    def execute(self, ctx: OperationContext, img: Image) -> Image:
        return img.replace_data(crop(img.data, self.box))

    def __str__(self):
        return f"Crop {self.box}"


