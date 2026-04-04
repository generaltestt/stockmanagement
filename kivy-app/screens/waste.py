from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class WasteScreen(Screen):
    message       = StringProperty('')
    mode          = StringProperty('def')   # 'def' or 'quality'
    product_id    = StringProperty('')
    product_name  = StringProperty('')
    product_price = NumericProperty(0.0)
    tray_size     = NumericProperty(1)
    

    def show_subscreen(self, name: str):
        self.ids.waste_sm.current = name

    def open_scanner(self):
        self.manager.scan_target_screen    = 'waste'
        self.manager.scan_target_subscreen = 'wasteScan'
        self.manager.scan_target_input     = 'barcode'
        self.manager.current = 'camera_scan'

    def set_barcode(self, code: str):
        if 'barcode' in self.ids:
            self.ids.barcode.text = code
        self.message = f'Scanned: {code}'

    def select_mode(self, mode: str):
        if self.summary_mode and mode == 'def':
            self.message = 'Finish/submit summary to use Date Expired'
            return
        self.mode = mode

    def backtoMenu(self):
        #self.reset_all()
        self.manager.current = 'menu'

    def continue_after_barcode(self):
        # Fetches product from API and shows the correct sub-screen
        app = self.manager.app
        upc = self.ids.barcode.text.strip()

        # Checks if UPC empty
        if not upc:
            self.message = 'Enter or scan a barcode'
            return
        
        # Retrieves product data from API
        data = app.api.get_product(upc)
        if data.get('error'): # error handling
            self.message = data['error']
            return
        
        # Store product details on WasteScreen
        self.product_id    = data.get('product_id', upc)
        self.product_name  = data.get('product_name', '')
        self.product_price = float(data.get('price', 0.0))
        self.tray_size     = int(data.get('tray_size', 1))
        self.qty_mode  = 'single'
        self.date_mode = 'today'
        self.message   = ''

        # If summary mode is active it always go to QW subscreen
        if self.summary_mode:
            self.mode == 'quality'
            self.show_subscreen('qualityWaste')
            return
        else: # if not, it goes to the correct subscreen
            if self.mode == 'def':
                self.show_subscreen('defWaste')
            else:
                self.show_subscreen('qualityWaste')
        
    def _parse_qty_int(self, text: str):
        t = (text or '').strip()
        if t == '':
            self.message = 'Enter a quantity'; return None
        try:
            q = int(t)
        except ValueError:
            self.message = 'Quantity must be an integer'; return None
        if q <= 0:
            self.message = 'Quantity must be > 0'; return None
        return q


    def select_date(self, mode: str):
        # Handles date toggle (pressing Tomorrow requires confirmation first)
        if mode == 'tomorrow' and not self.tomorrow_unlocked:
            # Shows confirmation before allowing reductions for tomorrow
            self._confirm_popup('Confirm', 'Unlock reductions for tomorrow?', on_yes=self._unlock_tomorrow)
            return
        self.date_mode = mode

    def _unlock_tomorrow(self):
        self.tomorrow_unlocked = True
        self.date_mode = 'tomorrow'

    def _confirm_popup(self, title: str, msg: str, on_yes):
        # Reusable Yes/No popup, calls on_yes() if Yes is pressed
        def yes(_btn): 
            pop.dismiss()
            on_yes()

        def no(_btn):
            pop.dismiss()

        # Configures layout for elements of popup
        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        box.add_widget(Label(text=msg, halign='center'))

        row = BoxLayout(size_hint_y=None, height=40, spacing=10)

        b1 = Button(text='Yes')
        b2 = Button(text='No')
        b1.bind(on_press=yes)
        b2.bind(on_press=no)

        row.add_widget(b1)
        row.add_widget(b2)
        box.add_widget(row)

        # Opens the popup
        pop = Popup(title=title, content=box, size_hint=(0.8, 0.42), auto_dismiss=False)
        pop.open()

    def confirm_and_waste_def(self):
        # Validates quantity input
        entered = self._parse_qty_int(self.ids.def_qty.text.strip())

        # Returns nothing if validation fails
        if entered is None: 
            return

        # Checks for tray sizes
        if self.qty_mode == 'tray':
            qty = entered * self.tray_size
        else:
            qty = entered
        
        # Popup asking to confirm submission
        self._confirm_popup('Confirm',
            f'Proceed with Date Expired Waste?\nUnits: {qty}\nDate: {self.date_mode}',
            on_yes=lambda: self._do_waste(qty))

    def _do_waste(self, qty: int):
        app = self.manager.app
        # Calls API to record waste for given product and quantity
        resp = app.api.waste(self.product_id, qty=qty)

        if resp.get('error'): # error handling
            self.message = resp['error']
            return
        
        # Returns user back to WasteScan with message and resets everything
        self.message = 'Waste recorded'
        self.reset_product_session()
        self.show_subscreen('wasteScan')

    def reset_product_session(self):
        # Clears product information ready for the next waste scan
        self.product_id = ''
        self.product_name = ''
        self.product_price = 0.0
        self.tray_size = 1
        self.qty_mode = 'single'
        self.date_mode = 'today'
        self.tomorrow_unlocked = False
        self.reduced_price = '£0.00'
        self.message           = ''
        #self.mode = 'def' # resets to default mode

        if 'barcode' in self.ids: 
            self.ids.barcode.text = ''
        if 'def_qty' in self.ids: 
            self.ids.def_qty.text = ''
        if 'q_qty'   in self.ids:
            self.ids.q_qty.text   = ''

    def quality_primary_action(self):
        if self.summary_update_mode: 
            self.update_entry_from_quality()
        elif self.summary_mode: 
            self.add_to_summary_quality()
        else: 
            self.confirm_and_waste_quality()

    def quality_secondary_action(self):
        if self.summary_update_mode:
            return
        if self.summary_mode:
            self.open_summary(from_product=True)
        else:
            self.add_to_summary_quality()

    def confirm_and_waste_quality(self):
        # Validates quantity input
        entered = self._parse_qty_int(self.ids.q_qty.text.strip())

        # Returns nothing if validation fails
        if entered is None: 
            return

        # Checks for tray sizes
        if self.qty_mode == 'tray':
            qty = entered * self.tray_size
        else:
            qty = entered

        # Popup asking to confirm submission
        self._confirm_popup('Confirm',
            f'Proceed with Quality Waste?\nUnits: {qty}',
            on_yes=lambda: self._do_waste(qty))

    def add_to_summary_quality(self):
        # Validates quantity input
        entered = self._parse_qty_int(self.ids.q_qty.text.strip())

        # Returns nothing if validation fails
        if entered is None: 
            return

        # Checks for tray sizes
        if self.qty_mode == 'tray':
            qty = entered * self.tray_size
        else:
            qty = entered
        
        # Appends to summary list
        self.summary_items.append({
            'product_id': self.product_id,
            'name':       self.product_name,
            'qty':        qty
        })

        # Switches to summary mode and goes back to the scan screen
        self.summary_items = list(self.summary_items)
        self.summary_mode = True
        self.message = 'Added to summary'
        self.reset_product_session()
        self.show_subscreen('wasteScan')

    def open_summary(self, from_product: bool = False):
        # Navigates to the summary screen and rebuilds the row widgets
        self.refresh_summary_ui()
        self.show_subscreen('summaryScreen')

    def refresh_summary_ui(self):
        # Rebuilds the scrollable list of summary rows
        box = self.ids.summary_list
        box.clear_widgets()

        # Loops through each item in the summary list and builds the row
        for idx, item in enumerate(self.summary_items):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=36, spacing=10)
            left = Label(
                text=f'{item["name"]} ({item["product_id"]})  x{item["qty"]}',
                halign='left', valign='middle'
            )
            left.bind(size=lambda inst, _v:
                      setattr(inst, 'text_size', (inst.width, None)))
            row.add_widget(left)
            box.add_widget(row)


    def summary_back(self):
        """Return from summary screen. Restore draft if came from product."""
        if (self.summary_return_to == 'qualityWaste'
                and self._quality_draft and not self.summary_update_mode):
            d = self._quality_draft
            self.product_id    = d['product_id']
            self.product_name  = d['product_name']
            self.product_price = d['product_price']
            self.tray_size     = d['tray_size']
            self.qty_mode      = d['qty_mode']
            if 'q_qty' in self.ids:
                self.ids.q_qty.text = d['q_qty']
        self.show_subscreen(self.summary_return_to)

    def refresh_summary_ui(self):
        """Rebuild the scrollable summary list from self.summary_items."""
        box = self.ids.summary_list
        box.clear_widgets()
        for idx, item in enumerate(self.summary_items):
            row = BoxLayout(orientation='horizontal',
                           size_hint_y=None, height=36, spacing=10)
            left = Label(
                text=f'{item["name"]} ({item["product_id"]})  x{item["qty"]}',
                halign='left', valign='middle'
            )
            left.bind(size=lambda inst, _v:
                      setattr(inst, 'text_size', (inst.width, None)))
            btn = Button(text=('Delete' if self.summary_delete_mode else 'Update'),
                         size_hint_x=None, width=90)
            btn.bind(on_press=lambda _b, i=idx: self.on_summary_row_button(i))
            row.add_widget(left); row.add_widget(btn)
            box.add_widget(row)

    def toggle_delete_mode(self):
        self.summary_delete_mode = not self.summary_delete_mode
        self.refresh_summary_ui()

    def on_summary_row_button(self, index: int):
        if self.summary_delete_mode:
            self._confirm_popup('Confirm', 'Delete this entry from the summary?',
                                on_yes=lambda: self._delete_summary_entry(index))
        else:
            self.start_update_entry(index)

    def _delete_summary_entry(self, index: int):
        if 0 <= index < len(self.summary_items):
            self.summary_items.pop(index)
            self.summary_items = list(self.summary_items)
            self.refresh_summary_ui()

    def start_update_entry(self, index: int):
        if not (0 <= index < len(self.summary_items)): return
        self.editing_index       = index
        self.summary_update_mode = True
        item = self.summary_items[index]
        data = self.manager.app.api.get_product(item['product_id'])
        if data.get('error'):
            self.message = data['error']
            self.summary_update_mode = False
            self.editing_index = -1
            return
        self.product_id    = data.get('product_id', item['product_id'])
        self.product_name  = data.get('product_name', item.get('name', ''))
        self.product_price = float(data.get('price', 0.0))
        self.tray_size     = int(data.get('tray_size', 1))
        self.qty_mode      = 'single'
        if 'q_qty' in self.ids:
            self.ids.q_qty.text = str(int(item['qty']))
        self.show_subscreen('qualityWaste')

    def update_entry_from_quality(self):
        if not (0 <= self.editing_index < len(self.summary_items)):
            self.summary_update_mode = False
            self.editing_index       = -1
            self.open_summary(from_product=False)
            return
        entered = self._parse_qty_int(self.ids.q_qty.text.strip())
        if entered is None: return
        if self.qty_mode == 'tray':
            qty = entered * self.tray_size
        else:
            qty = entered
        
        self.editing_index = -1 # resets after
        self.summary_items[self.editing_index]['qty'] = qty # updates first
        self.summary_items = list(self.summary_items)
        self.summary_update_mode = False
            
        self.refresh_summary_ui()
        self.show_subscreen('summaryScreen')
#####
    def toggle_delete_mode(self):
        # Changes delete mode to on/off and refreshes summary UI buttons
        self.summary_delete_mode = not self.summary_delete_mode
        self.refresh_summary_ui()

    def on_summary_row_button(self, index: int):
        # If buttons are delete it shows a popup, if it's update it shows the update screen
        if self.summary_delete_mode:
            self._confirm_popup('Confirm', 'Delete this entry from the summary?',
                on_yes= self._delete_summary_entry(index))
        else:
            self.start_update_entry(index)

    def _delete_summary_entry(self, index: int):
        if 0 <= index < len(self.summary_items): # prevents IndexErrors
            self.summary_items.pop(index) # deletes entry
            self.summary_items = list(self.summary_items)
            self.refresh_summary_ui() # refreshes UI again

    def start_update_entry(self, index: int):
        # Loads a summary entry into the quality subscreen for editing
        if not (0 <= index < len(self.summary_items)): 
            return
        self.editing_index      = index
        self.summary_update_mode = True
        item = self.summary_items[index]

        # Fetches product information for the update screen
        data = self.manager.app.api.get_product(item['product_id'])
        if data.get('error'): # error handling
            self.message = data['error']
            self.summary_update_mode = False
            self.editing_index = -1
            return
        
        # Displays product information
        self.product_id   = data.get('product_id',   item['product_id'])
        self.product_name = data.get('product_name', item.get('name', ''))
        self.product_price = float(data.get('price',    0.0))
        self.tray_size     = int(data.get('tray_size', 1))
        self.qty_mode = 'single'

        # Displays the old quantity so the user can edit
        if 'q_qty' in self.ids:
            self.ids.q_qty.text = str(int(item['qty']))
        
        self.show_subscreen('qualityWaste') # Shows the update screen

    def update_entry_from_quality(self):
        # Saves the edited quantity back into the summary list
        if not (0 <= self.editing_index < len(self.summary_items)):
            self.summary_update_mode = False
            self.editing_index = -1
            self.open_summary(from_product=False)
            return

        # Validates quantity input
        entered = self._parse_qty_int(self.ids.q_qty.text.strip())

        # Returns nothing if validation fails
        if entered is None: 
            return

        # Checks for tray sizes
        if self.qty_mode == 'tray':
            qty = entered * self.tray_size
        else:
            qty = entered
        
        # Updates entry
        self.summary_items = list(self.summary_items)
        self.summary_update_mode = False
        self.editing_index = -1
        self.summary_items[self.editing_index]['qty'] = qty

        self.open_summary(from_product=False) # opens summary again

    def quality_primary_action(self):
        # Controls what the primary button on the QW screen does
        if self.summary_update_mode:
            self.update_entry_from_quality()
        elif self.summary_mode:
            self.add_to_summary_quality()
        else:
            self.confirm_and_waste_quality()

    def confirm_submit_summary(self):
        # Checks if summary list is empty
        if not self.summary_items:
            self.message = 'Summary is empty'
            return
        
        # Shows popup confirmation
        count = len(self.summary_items) # counts how many items are in the list
        self._confirm_popup('Confirm', f'Submit {count} item(s) in the summary?',
            on_yes=self.submit_summary)

    def submit_summary(self):
        # Checks again if summary list is empty
        if not self.summary_items:
            self.message = 'Summary is empty'
            return
        
        # Loops through each item in the summary list and sends an API waste request
        app = self.manager.app
        for item in self.summary_items:
            resp = app.api.waste(item['product_id'], qty=item['qty'])
            if resp.get('error'):
                self.message = f'Failed {item["product_id"]}: {resp["error"]}'
            self.reset_product_session()
        
        # Resets summary list
        self.summary_items = []
        self.summary_mode  = False
        self.message       = 'Summary submitted'

        self.show_subscreen('wasteScan') # shows scan screen 

    def reset_all(self):
        # Clears summary variables and states first
        self.summary_mode = False
        self.summary_items = []
        self.summary_delete_mode = False
        self.summary_update_mode = False
        self.editing_index = -1
        self._quality_draft = None
        self.message = ''
        # Clears product session
        self.reset_product_session()
        # Makes sure subscreen set is wastescan
        self.show_subscreen('wasteScan')

    def backtoMenu(self):
        self.reset_all() # full reset when leaving the waste program
        self.manager.current = 'menu'


        
    qty_mode      = StringProperty('single')
    date_mode     = StringProperty('today')
    tomorrow_unlocked = BooleanProperty(False)
    reduced_price = StringProperty('£0.00')
    summary_mode  = BooleanProperty(False)
    summary_items = ListProperty([])
    summary_return_to    = StringProperty('wasteScan')
    summary_delete_mode  = BooleanProperty(False)
    summary_update_mode  = BooleanProperty(False)
    editing_index        = NumericProperty(-1)
    _quality_draft       = None