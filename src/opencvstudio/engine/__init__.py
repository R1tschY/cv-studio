from functools import reduce
from typing import Optional

from opencvstudio.opmodel import Operation, OperationContext
from opencvstudio.primitives.image import Image


class Engine:

    def __init__(self, ctx: OperationContext):
        self.ctx = ctx
        self.steps = []
        self.input = None

    def set_input(self, input: Optional[Image]):
        self.input = input

    def add_operation(self, operation: Operation) -> None:
        self.steps.append(OperationStep(operation))

    def __getitem__(self, item):
        return self.steps[item]

    @property
    def output(self) -> Optional[Image]:
        return self.input if not self.steps else self.steps[-1].result

    def update(self):
        if self.input is not None:
            img = self.input
            for step in self.steps:
                img = step.execute(self.ctx, img)
        else:
            for step in self.steps:
                step.result = None


class OperationStep:
    """
    Wrapper for `Operation`
    """

    def __init__(self, operation: Operation, result: Image = None):
        self.operation = operation
        self.result = result

    def execute(self, ctx: OperationContext, img: Image) -> Image:
        self.result = self.operation.execute(ctx, img)
        return self.result
