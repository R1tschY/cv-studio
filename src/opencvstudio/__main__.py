import sys

import gi
gi.require_version("Gtk", "3.0")

# noinspection PyUnresolvedReferences
from gi.repository import Gtk

from opencvstudio.application import Application

app = Application()
app.run(sys.argv)
