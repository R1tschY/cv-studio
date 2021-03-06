from gi.repository import GLib, GdkPixbuf, Gio, Gtk


# list of tuples for each software, containing the software name, initial release, and main programming languages used
from opencvstudio.dataops import open_image
from opencvstudio.engine import Engine
from opencvstudio.ui.gtkhelper import run_dialog
from opencvstudio.opmodel import OperationContext
from opencvstudio.ops.box_ops import CropOp
from opencvstudio.primitives import Box
from opencvstudio.primitives.color import ColorSpace
from opencvstudio.primitives.image import Image
from opencvstudio.ui.imageview import ImageView
from opencvstudio.ui.opstore import OpStore
from opencvstudio.version import PRODUCT_NAME


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, application):
        super().__init__(title=PRODUCT_NAME, application=application)
        self.set_border_width(10)
        self.set_size_request(750, 500)

        # Header
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "OpenCV Studio"
        self.set_titlebar(header)

        # Menu
        menubutton = Gtk.MenuButton()
        menubutton.set_size_request(35, 35)
        header.pack_end(menubutton)

        self._init_actions()

        menumodel = self.create_main_menu()

        # the menu is set as the menu of the menubutton
        menubutton.set_menu_model(menumodel)

        # Creating the ListStore model
        self.engine = Engine(OperationContext())
        self.liststore = OpStore(self.engine)

        self.treeview = Gtk.TreeView.new_with_model(self.liststore)
        for i, column_title in enumerate(["Operationen"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        select = self.treeview.get_selection()
        select.connect("changed", self.on_selection_changed)

        # Sidebar
        self.sidebar = Gtk.HPaned.new()
        self.sidebar.set_position(200)

        # Test-View
        self.view = ImageView()
        self.view.set_size_request(width=400, height=400)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.add(self.treeview)
        self.sidebar.add1(self.scrollable_treelist)

        self.scrollable_view = Gtk.ScrolledWindow()
        self.scrollable_view.set_vexpand(True)
        self.scrollable_view.set_hexpand(True)
        self.scrollable_view.add(self.view)
        self.sidebar.add2(self.scrollable_view)

        self.add(self.sidebar)
        self.show_all()

    def create_main_menu(self):
        menumodel = Gio.Menu()
        menumodel.append("Open image", "win.open-image")
        menumodel.append("About", "win.about")
        menumodel.append("Quit", "app.quit")

        submenu = Gio.Menu()
        submenu.append("Cut", "win.add-cut")
        menumodel.append_submenu("Operations", submenu)

        return menumodel

    def _init_actions(self):
        # Cut
        cut_action = Gio.SimpleAction.new("add-cut", None)
        cut_action.connect("activate", self.on_cut_op)
        self.add_action(cut_action)

        open_image_action = Gio.SimpleAction.new("open-image", None)
        open_image_action.connect("activate", self.on_open_image)
        self.add_action(open_image_action)

    def on_cut_op(self, a, b):
        print(f"on_cut_op({a}, {b})")
        self.liststore.append(CropOp(Box(50, 50, 500, 500)))
        self.update_image()

    def on_open_image(self, action, params):
        dialog = Gtk.FileChooserDialog(
            title="Choose image to use as tests", parent=self,
            action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        with run_dialog(dialog) as response:
            if response == Gtk.ResponseType.OK:
                self.set_test_input(
                    Image(open_image(dialog.get_filename()), ColorSpace.BGR))
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")

    def on_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", model[treeiter][0])

        self.update_image(treeiter)

    def set_test_input(self, image: Image):
        if image is not None:
            self.engine.set_input(image)

            self.update_image()

    def update_image(self, selection=None):
        self.engine.update()

        if selection is None:
            output = self.engine.output
        else:
            output = None

        if output is not None:
            img = output.convert_color(ColorSpace.RGB)
            # TODO: new_from_data
            bytes = GLib.Bytes.new(output.data.tobytes())
            pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
                bytes, GdkPixbuf.Colorspace.RGB, False, 8,
                img.size[1], img.size[0], img.size[1] * 3)
            self.view.set_from_pixbuf(pixbuf)
