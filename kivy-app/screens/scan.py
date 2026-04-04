from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

class ScanScreen(Screen):
    message = StringProperty('')

    def open_scanner(self):
        """Set routing on ScreenManager then open the camera screen."""
        sm = self.manager
        sm.scan_target_screen = 'scan'    # return here after scan
        sm.scan_target_input  = 'barcode' # fill this widget id
        sm.current = 'camera_scan'

    def set_barcode(self, code: str):
        """Receives the scanned barcode string from CameraScanScreen."""
        self.ids.barcode.text = code
        self.message = f'Scanned: {code}'

    def lookup(self):
        # Calls the backend and shows ProductScreen if successful
        app = self.manager.app
        barcode = self.ids.barcode.text.strip()

        # Makes sure barcode is not empty
        if not barcode:
            self.message = 'Enter a barcode'
            return
        
        # Calls API to fetch product data using the barcode
        data = app.api.get_product(barcode)

        # Checks if API returned an error
        if data.get('error'):
            err = data['error'].lower()
            # Differentiates 'not in database' from 'server unreachable'
            if 'not found' in err:
                self.message = 'Product not found. Check the barcode.'
            else:
                self.message = 'Could not reach the server. Try again.'
            return  # stops execution if error


        # Populates ProductScreen with data before showing the screen
        product_screen = self.manager.get_screen('product')
        product_screen.set_product(data)
        self.message = ''
        self.manager.current = 'product'

    def backtoMenu(self):
        """Return to the main menu and clear any error message."""
        self.message = ''
        self.manager.current = 'menu'
