from gi.repository import Gtk


class ImageView(Gtk.Image):

    def __init__(self, *args, **kwargs):
        super(ImageView, self).__init__(*args, **kwargs)

