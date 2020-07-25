from contextlib import contextmanager

from gi.repository.Gtk import Dialog, ResponseType


@contextmanager
def run_dialog(dialog: Dialog) -> ResponseType:
    yield dialog.run()
    dialog.destroy()
