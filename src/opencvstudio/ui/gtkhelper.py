from contextlib import contextmanager

from gi.repository import GdkPixbuf
from gi.repository.Gtk import Dialog, ResponseType
from opencvstudio.primitives.image import Image


@contextmanager
def run_dialog(dialog: Dialog) -> ResponseType:
    try:
        yield dialog.run()
    finally:
        dialog.destroy()


def pixbuf_from_image(img: Image):
    GdkPixbuf.Colorspace.RGB
    return GdkPixbuf.Pixbuf.new_from_bytes(img.data)
