

class AbstractListModel:
    def row_count(self):
        raise NotImplementedError

    def data(self, row: int, column: int):
        raise NotImplementedError
