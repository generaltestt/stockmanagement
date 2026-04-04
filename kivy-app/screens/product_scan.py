from kivy.uix.screenmanager import Screen
from kivy.properties import (StringProperty, NumericProperty,
                              BooleanProperty, ListProperty, DictProperty)
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App

class StockCountScreen(Screen):
    message              = StringProperty('')
    multi_mode           = BooleanProperty(False)
    scanned_items        = ListProperty([])  # {product_id,name,tray_size,included}
    recently_scanned_id  = StringProperty('')
    recently_scanned_name = StringProperty('')
    section              = StringProperty('stockroom')
    qty_mode             = StringProperty('single')
    tray_size            = NumericProperty(1)
    product_index        = NumericProperty(0)
    total_products       = NumericProperty(0)
    product_id           = StringProperty('')
    product_name         = StringProperty('')
    counts               = DictProperty({})  # counts[pid]={'stockroom':0,'shopfloor':0}
    queue                = ListProperty([])
    in_progress          = BooleanProperty(False)

    def show_subscreen(self, name: str):
        self.ids.count_sm.current = name

    def back_to_menu(self):
        self.reset_all()
        self.manager.current = 'menu'

    def open_scanner_single(self):
        self.manager.scan_target_screen    = 'stock_count'
        self.manager.scan_target_subscreen = 'scanSingle'
        self.manager.scan_target_input     = 'single_barcode'
        self.manager.current = 'camera_scan'

    def set_barcode(self, code: str):
        if self.ids.count_sm.current == 'scanMulti':
            self.ids.multi_barcode.text = code
            self.add_scanned_from_multi_input()  # auto-add on multi screen
        else:
            self.ids.single_barcode.text = code
