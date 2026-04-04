from kivy.uix.screenmanager import Screen
from kivy.properties import (StringProperty, NumericProperty, BooleanProperty, ListProperty, DictProperty)
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App

class StockCountScreen(Screen):
    def show_subscreen(self, name):
        # Changes subscreen in the stock count screen
        self.ids.count_sm.current = name

    def back_to_menu(self):
        # Resets everything before exiting
        self.reset_all()
        self.manager.current = 'menu'

    def open_scanner_single(self):
        # Sets screen and subscreen to return to after scan
        self.manager.scan_target_screen    = 'stock_count'
        self.manager.scan_target_subscreen = 'scanSingle'
        self.manager.current = 'camera_scan' # opens scanner

    def set_barcode(self, code: str):
        # Handles barcode scanned
        if self.ids.count_sm.current == 'scanMulti':
            self.ids.multi_barcode.text = code
            self.add_scanned_from_multi_input()  # auto adds on multi screen
        else:
            self.ids.single_barcode.text = code

    ####

    def continue_single(self):
        # Fetches product and starts the product counting
        upc = self.ids.single_barcode.text.strip()

        # Validates the input
        if not upc:
            self.message = 'Enter or scan a UPC'
            return
        
        # Sends barcode to API
        data = App.get_running_app().api.get_product(upc)

        # Displays error if API returns one
        if data.get('error'):
            self.message = data['error']
            
        # Adds product data to items
        items = [{
            'product_id': data.get('product_id', upc),
            'name':       data.get('product_name', ''),  # correct key
            'tray_size':  int(data.get('tray_size', 1)),
        }]

        self._prepare_counting(items) # prepares next screen
        self.multi_mode = False  # hides Product x of x label
        self.show_subscreen('counting') # shows next screen

    def _prepare_counting(self, items):
        # Sets variables for counting session
        self.in_progress = True
        self.queue = items
        self.total_products = len(items)
        self.product_index = 0
        self.section = 'stockroom'
        self.qty_mode = 'single'

        # Sets count for each item
        self.counts = {}
        for item in items:
            self.counts[item['product_id']] = {
                'stockroom': 0,
                'shopfloor': 0}
        
        # Loads first product
        self._load_current_product()

    def _load_current_product(self):
        # Gets current product from queue
        item = self.queue[self.product_index]

        # Stores product details
        self.product_id   = item['product_id']
        self.product_name = item['name']
        self.tray_size    = int(item.get('tray_size', 1))

        # Updates UI with product details
        self._load_current_product_into_box()

    def _load_current_product_into_box(self):
        # Makes sure UI elements exist and product is set
        if 'count_qty' not in self.ids or not self.product_id: 
            return
        current = int(self.counts[self.product_id][self.section])

        # Shows empty if zero
        if current == 0:
            self.ids.count_qty.text = '' 
        else:
            self.ids.count_qty.text = str(current)
##################


    def save_current(self):
        # Gets text input, blank is '' to avoid errors
        t = (self.ids.count_qty.text or '').strip()

        # Converts to integer or sets blank to 0
        try:
            if t != '':
                entered = int(t)
            else:
                entered = 0
        except ValueError: # if entered isn't an integer or blank
            self.message = 'Quantity must be an integer'
            entered = 0

        # If quantity mode is tray, quantity gets multiplied by tray size
        if self.qty_mode == 'tray':
            eff = entered * self.tray_size
        else:
            eff = entered

        # Stores the quantity for the current product/section
        self.counts[self.product_id][self.section] = int(eff)

    def next_section_single(self):
        # Next section / finish for single mode
        self.save_current()  # saves before navigating sections

        # If stockroom, moves to next section
        if self.section == 'stockroom':
            self.section = 'shopfloor'
            self._load_current_product_into_box()
        else: # If shopfloor, it submits with confirmation popup
            self.confirm_finish_single()

    def confirm_finish_single(self):
        # Combines the stockroom and shopfloor total for the current product
        pid   = self.product_id
        total = (int(self.counts[pid]['stockroom']) + int(self.counts[pid]['shopfloor']))
        self._confirm_popup('Confirm', f'Submit total count {total} for 1 product?',
            self._submit_counts)

    def _submit_counts(self):
        # Builds the payload by combining the two section counts for each product
        items = []
        for it in self.queue:
            pid   = it['product_id']
            total = int(self.counts[pid]['stockroom']) + int(self.counts[pid]['shopfloor'])
            items.append({'product_id': pid, 'total': total})
        
        # Sends counts to API
        resp = App.get_running_app().api.submit_stock_counts(items)

        # Error handling
        if resp.get('error'): 
            self.message = resp['error']
            return
        
        # Resets and goes back to the scan screen
        self.reset_all()
        self.show_subscreen('scanSingle')

    def select_qty_mode(self, mode: str):
        self.qty_mode = mode

    def _confirm_popup(self, title: str, msg: str, on_yes):
        def yes(_btn): pop.dismiss(); on_yes()
        def no(_btn):  pop.dismiss()
        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        box.add_widget(Label(text=msg, halign='center'))
        row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        b1 = Button(text='Yes'); b2 = Button(text='No')
        b1.bind(on_press=yes); b2.bind(on_press=no)
        row.add_widget(b1); row.add_widget(b2)
        box.add_widget(row)
        pop = Popup(title=title, content=box, size_hint=(0.8, 0.42), auto_dismiss=False)
        pop.open()
#########################

    def start_multi_scan(self):
        # Resets everything to start a fresh session
        self.reset_all()
        self.multi_mode = True
        self.show_subscreen('scanMulti')

    def open_scanner_multi(self):
        # Tells the camera screen where to return back to
        self.manager.scan_target_screen    = 'stock_count'
        self.manager.scan_target_subscreen = 'scanMulti'
        self.manager.scan_target_input     = 'multi_barcode'
        self.manager.current = 'camera_scan'

    def add_scanned_from_multi_input(self):
        # Gets text input from barcode field
        upc = self.ids.multi_barcode.text.strip()
        if not upc: 
            return # ignores empty input
        
        # Looks up the product from the API
        data = App.get_running_app().api.get_product(upc)

        # Error handling
        if data.get('error'): 
            self.message = data['error']
            return
        pid = data.get('product_id', upc)

        # Prevents duplicate products in the list
        for item in self.scanned_items:
            if item['product_id'] == pid:
                self.message = 'Already in list'
                self.ids.multi_barcode.text = ''

        # Builds the item record and adds it to the scanned list
        it = {'product_id': pid,
              'name':       data.get('product_name', ''),
              'tray_size':  int(data.get('tray_size', 1)),
              'included':   True}
        self.scanned_items.append(it) # adds to scanned items list
    
        self.recently_scanned_id   = it['product_id']
        self.recently_scanned_name = it['name']
        self.ids.multi_barcode.text = ''
        self.message = ''
        self.refresh_multi_list()

    def toggle_include(self, idx: int):
        if 0 <= idx < len(self.scanned_items):
            self.scanned_items[idx]['included'] = \
                not self.scanned_items[idx].get('included', True)
            self.scanned_items = list(self.scanned_items)
            self.refresh_multi_list()

    def refresh_multi_list(self):
        if 'multi_list' not in self.ids: return
        box = self.ids.multi_list
        box.clear_widgets()
        for idx, item in enumerate(self.scanned_items):
            row = BoxLayout(orientation='horizontal',
                           size_hint_y=None, height=44, spacing=10)
            included = item.get('included', True)
            name_upc = item['name'] + chr(10) + 'UPC: ' + item['product_id']
            lbl = Label(text=name_upc, halign='left', valign='middle')
            lbl.bind(size=lambda inst,_v:
                     setattr(inst, 'text_size', (inst.width, None)))
            if not included: lbl.color = (0.6, 0.6, 0.6, 1)  # grey out
            btn = Button(text=('X' if included else '+'),
                         size_hint_x=None, width=60)
            # i=idx captures by value - avoids closure bug
            btn.bind(on_press=lambda _b, i=idx: self.toggle_include(i))
            row.add_widget(lbl); row.add_widget(btn)
            box.add_widget(row)

    def continue_multi_to_counting(self):
        included = [x for x in self.scanned_items if x.get('included', True)]
        if not included: self.message = 'No products selected'; return
        self._prepare_counting(included)
        self.multi_mode = True
        self.show_subscreen('counting')
    def reset_all(self):
        self.in_progress=False; self.message=''; self.multi_mode=False
        self.scanned_items=[]; self.recently_scanned_id=''; self.recently_scanned_name=''
        self.section='stockroom'; self.qty_mode='single'; self.tray_size=1
        self.product_index=0; self.total_products=0; self.product_id=''; self.product_name=''
        self.counts={}; self.queue=[]
        if 'single_barcode' in self.ids: self.ids.single_barcode.text=''
        if 'multi_barcode'  in self.ids: self.ids.multi_barcode.text=''
        if 'count_qty'      in self.ids: self.ids.count_qty.text=''
        if 'multi_list' in self.ids: self.refresh_multi_list()

    def next_product(self):
        # Multi product mode's primary button which advances to next product or section
        self.save_current()  # always saves before moving

        # Loads any more products that remain in this section
        if self.product_index < self.total_products - 1:
            self.product_index += 1
            self._load_current_product()
            return

        # If no more products, continues to next section or submits
        if self.section == 'stockroom':
            self.section = 'shopfloor'
            self.product_index = 0
            self._load_current_product()
        else:
            self.confirm_submit_counts()

    def skip_to_next_section(self):
        # Zeros remaining products in the section and moves on
        self.save_current()  # saves current product

        # Loops through remaining products
        for i in range(self.product_index + 1, self.total_products):
            pid = self.queue[i]['product_id']
            self.counts[pid][self.section] = 0 # zeroes the product

        # Continues to next section or submits
        if self.section == 'stockroom':
            self.product_index = 0
            self.section = 'shopfloor' # sets before loading
            self._load_current_product() # now loads shopfloor = 0
        else:
            self.confirm_submit_counts()

    def confirm_submit_counts(self):
        # Shows confirmation popup with total number of products before submitting
        n = self.total_products
        self._confirm_popup('Confirm', f'Submit {n} product(s)?', self._submit_counts)
################
    def exit_flow(self):
        # Warns user before discarding all unsaved counts
        self._confirm_popup('Confirm', 'Exit counting? Unsaved changes will be lost.', self.exit_to_scan)

    def exit_to_scan(self):
        # If confirmed, user is returned to the single scan screen
        self.show_subscreen('scanSingle')

    def back_from_counting(self):
        # Goes back to previous section
        if self.section == 'shopfloor':
            self.section = 'stockroom'
            self._load_current_product_into_box() # shows quantity input for stockroom
            return
        
        # If on stockroom, shows popup to exit
        self._confirm_popup('Confirm', 'Go back? Unsaved changes will be lost.', self._back_now)

    def _back_now(self):
        # Returns to whichever scan screen launched the counting session
        if self.multi_mode:
            self.show_subscreen('scanMulti')
        else:
            self.show_subscreen('scanSingle')

    def back_to_scan_single(self):
        # Resets the session and returns to start
        self.reset_all()
        self.show_subscreen('scanSingle')

    def reset_all(self):
        # Resets all variables
        self.in_progress = False
        self.message = ''
        self.multi_mode = False
        self.scanned_items = []
        self.recently_scanned_id = ''
        self.recently_scanned_name = ''
        self.section = 'stockroom'
        self.qty_mode = 'single'
        self.tray_size = 1
        self.product_index = 0
        self.total_products = 0
        self.product_id = ''
        self.product_name = ''
        self.counts = {}
        self.queue = []

        # Resets UI inputs
        self.ids.single_barcode.text = ''
        self.ids.multi_barcode.text = ''
        self.ids.count_qty.text = ''
        self.refresh_multi_list()  # clears the GridLayout widget

    message = StringProperty('')
    multi_mode = BooleanProperty(False)
    scanned_items = ListProperty([])
    recently_scanned_id = StringProperty('')
    recently_scanned_name = StringProperty('')
    section = StringProperty('stockroom')
    qty_mode = StringProperty('single')
    tray_size = NumericProperty(1)
    product_index =  NumericProperty(0)
    total_products = NumericProperty(0)
    product_id = StringProperty('')
    product_name = StringProperty('')
    counts = DictProperty({})
    in_progress = BooleanProperty(False)

