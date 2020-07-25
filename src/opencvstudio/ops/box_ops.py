from opencvstudio.opmodel import Operation, OperationContext, Parameter
from opencvstudio.primitives.image import Image
from opencvstudio.primitives import Box


class CropOp(Operation):

    @classmethod
    def parameters(cls):
        return [
            Parameter("box", Box, lambda img: Box.from_size(img.size))
        ]

    def __init__(self, box: Box):
        self.box = box

    def execute(self, ctx: OperationContext, img: Image) -> Image:
        return img.cut(self.box)


