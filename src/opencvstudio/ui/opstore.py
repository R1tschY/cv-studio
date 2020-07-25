from typing import Tuple

from gi.repository import Gtk
from opencvstudio.engine import Engine, OperationStep
from opencvstudio.opmodel import Operation, OperationContext


class OpStore(Gtk.ListStore):  # TODO: use gtk.TreeModel
    def __init__(self, engine: Engine):
        super().__init__(str)
        self._model = engine

    def append(self, operation: Operation) -> None:
        self._model.add_operation(operation)
        super().append(self._data(self._model[-1]))

    def changed(self, row: int) -> None:
        self[(row,)] = self._data(self._model[row])

    def _data(self, step: OperationStep) -> Tuple:
        return (str(step.operation),)
