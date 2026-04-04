from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

class ProductScreen(Screen):
    title   = StringProperty('')
    details = StringProperty('')

    def set_product(self, data: dict):
        pid   = data.get('product_id', '')
        name  = data.get('product_name', '')
        price = data.get('price', 0)
        stock = data.get('stock_amount', 0)
        cap   = data.get('capacity', 0)
        tray  = data.get('tray_size', 1)
        self.title = name or 'Product'
        self.details = (
            f'UPC: {pid}\n'
            f'Price: £{float(price):.2f}\n'
            f'Stock (store): {stock}\n'
            f'Shelf capacity: {cap}\n'
            f'Tray size: {tray}'
        )

    def back_to_scan(self):
        self.manager.current = 'scan'
