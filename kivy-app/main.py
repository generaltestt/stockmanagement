from kivy_garden.zbarcam import ZBarCam
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition

from api import ApiClient
from screens.login import LoginScreen

from kivy.uix.screenmanager import ScreenManager
from screens.login import LoginScreen
from screens.menu import MenuScreen
from screens.scan import ScanScreen # Added the import
from screens.camera_scan import CameraScanScreen

from screens.product import ProductScreen  # product detail screen
from screens.waste import WasteScreen
from screens.stock_count import StockCountScreen



KV = """
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import ZBarCam kivy_garden.zbarcam.ZBarCam

ScreenManager:
    LoginScreen:
        name: "login"
    MenuScreen:
        name: "menu"
    ScanScreen:
        name: "scan"
    CameraScanScreen:
        name: "camera_scan"
    ProductScreen:
        name: "product"
    WasteScreen:
        name: "waste"
    StockCountScreen:
        name: "stock_count"
    

# KV string - defines the UI layout for the LoginScreen.
# BoxLayout stacks widgets vertically top-to-bottom.
<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 10
# Store Section:
        BoxLayout:
            id: store_section
            orientation: 'vertical'
            Label:
                text: 'Store Login'
            TextInput:
                id: store_search
                on_text: root.on_store_text(self.text)
            Button:
                text: 'Continue'
                on_press: root.check_store()
# Login Section (hidden initially):
        BoxLayout:
            id: login_section
            orientation: 'vertical'
            opacity: 0
            disabled: True
            Label:
                id: store_label
            TextInput:
                id: username
                hint_text: 'Colleague ID'
            TextInput:
                id: password
                hint_text: 'Password'
                password: True
            Button:
                text: 'Login'
                on_press: root.do_login()
            Button:
                text: 'Back'
                on_press: root.back_to_store_login()



        # ── error label shown in both sections ──
        Label:
            text: root.message
            color: 1, 0, 0, 1
            size_hint_y: None
            height: '20sp'

<MenuScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 10

        BoxLayout:
            size_hint_y: None
            height: 44
            Label:
                text: root.welcome_text
                font_size: 20
                halign: "left"
                valign: "middle"
                text_size: self.size
            Label:
                text: root.today_text
                size_hint_x: None
                width: 80
            Button:
                text: "Sign out"
                size_hint_x: None
                width: 90
                on_press: root.sign_out()

        Button:
            text: "Product Lookup"
            size_hint_y: None
            opacity: 1 if root.show_store_features else 0
            disabled: False if root.show_store_features else True
            height: 48 if root.show_store_features else 0
            on_press: root.menuLookup()
        
        Button:
            text: "Waste"
            size_hint_y: None
            opacity: 1 if root.show_store_features else 0
            disabled: False if root.show_store_features else True
            height: 48 if root.show_store_features else 0
            on_press: root.menuWaste()
        
        Button:
            text: "Stock Counting"
            size_hint_y: None
            opacity: 1 if root.show_store_features else 0
            disabled: False if root.show_store_features else True
            height: 48 if root.show_store_features else 0
            on_press: root.menuCount()

<CameraScanScreen>:
    BoxLayout:
        orientation: 'vertical'
        ZBarCam:
            id: zbarcam 
            # on_symbols fires every frame a barcode is detected
            on_symbols: root.on_code_scanned()
        Button:
            text: 'Cancel'
            size_hint_y: None
            height: '48sp'
            on_press: root.go_back(None)  # None = cancelled so no code


<ScanScreen>:
    BoxLayout:
        orientation: 'vertical'   # top-to-bottom stacking
        padding: 30
        spacing: 12
        Label:
            text: 'Product Lookup'
            font_size: '22sp'
            size_hint_y: None
            height: '40sp'
        # barcode TextInput - filled by typing or by camera scan
        TextInput:
            id: barcode
            hint_text: 'Barcode'
            size_hint_y: None
            height: '44sp'
        BoxLayout:
            size_hint_y: None
            height: '48sp'
            spacing: 8
            Button:
                text: 'Scan'
                on_press: root.open_scanner()  # wired up in iteration 2
            Button:
                text: 'Look Up'
                on_press: root.lookup()        # wired up in iteration 5
        Label:
            text: root.message  # red status/error label
            color: 1, 0, 0, 1
        Button:
            text: 'Back'
            size_hint_y: None
            height: '44sp'
            on_press: root.backtoMenu()

<ProductScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 12
        # product name displayed as a prominent heading
        Label:
            text: root.title
            font_size: '20sp'
            bold: True
            size_hint_y: None
            height: '44sp'
        # multi-line details block - shows UPC, price, stock etc.
        Label:
            text: root.details
            font_size: '16sp'
            text_size: self.width, None  # enables word wrap
            halign: 'left'
        Button:
            text: 'Back'
            size_hint_y: None
            height: '44sp'
            on_press: root.back_to_scan()

# Uses a nested ScreenManager for its four subscreens to avoid cluttering
<WasteScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        ScreenManager:
            id: waste_sm

# Subscreen 1 - barcode entry + mode selection:
            Screen:
                name: 'wasteScan'
                BoxLayout:
                    orientation: 'vertical'      # stacks elements vertically
                    spacing: 10
                    Label:
                        text: 'Waste'
                        font_size: 28
                        size_hint_y: None # fixed height
                        height: 50

                    # Mode toggle row (switches between DEF and Quality modes)
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Date Expired'
                            on_press: root.select_mode('def')     # Sets mode to DEF
                            # Black background when selected, white otherwise
                            background_color: (0,0,0,1) if root.mode == 'def' else (1,1,1,1)
                            color: (1,1,1,1)
                        Button:
                            text: 'Quality'
                            on_press: root.select_mode('quality')    # Sets mode to Quality Waste
                            background_color: (0,0,0,1) if root.mode == 'quality' else (1,1,1,1)
                            color: (1,1,1,1)

                    TextInput:
                        id: barcode
                        hint_text: 'Product number / barcode'    # Barcode scanning / UPC entering
                        multiline: False
                        size_hint_y: None
                        height: 44
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Scan'
                            on_press: root.open_scanner()      # Opens the camera
                        Button:
                            text: 'Continue'
                            on_press: root.continue_after_barcode()

                        # Only visible when 
                        Button:
                            text: 'View Summary'
                            size_hint_y: None
                            height: 48
                            opacity: 1 if root.summary_mode else 0
                            disabled: False if root.summary_mode else True
                            on_press: root.open_summary(from_product=False)

                    Label:
                        text: root.message      # Error messages
                        color: (1,0,0,1)
                    Button:
                        text: 'Back to Menu'
                        size_hint_y: None
                        height: 48
                        on_press: root.backtoMenu()    # Goes back to main menu
            Screen:
                name: 'defWaste'
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Back'
                            size_hint_x: None
                            width: 100
                            on_press: root.show_subscreen('wasteScan')   # Goes back to scan screen
                        Label:
                            text: 'Date Expired Waste'
                            font_size: 20
                    Label:
                        text: 'UPC: ' + root.product_id
                    Label:
                        text: root.product_name
                    Label:
                        text: 'Price: £' + '{:.2f}'.format(root.product_price)

                    # Date toggle: Today / Tomorrow
                    Label:
                        text: 'Date'
                        size_hint_y: None
                        height: 24
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Today'
                            on_press: root.select_date('today')
                            background_color: (0,0,0,1) if root.date_mode=='today' else (1,1,1,1)
                            color: (1,1,1,1) if root.date_mode=='today' else (0,0,0,1)
                        Button:
                            text: 'Tomorrow'
                            on_press: root.select_date('tomorrow')
                            background_color: (0,0,0,1) if root.date_mode=='tomorrow' else (1,1,1,1)
                            color: (1,1,1,1) if root.date_mode=='tomorrow' else (0,0,0,1)
                    # Quantity mode toggle: Single / Tray
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Single'
                            on_press: root.select_qty_mode('single')
                            background_color: (0,0,0,1) if root.qty_mode=='single' else (1,1,1,1)
                            color: (1,1,1,1) if root.qty_mode=='single' else (0,0,0,1)
                        Button:
                            text: 'Tray'
                            on_press: root.select_qty_mode('tray')
                            background_color: (0,0,0,1) if root.qty_mode=='tray' else (1,1,1,1)
                            color: (1,1,1,1) if root.qty_mode=='tray' else (0,0,0,1)
                        Label:
                            text: 'Tray: ' + str(root.tray_size)
                    TextInput:
                        id: def_qty
                        hint_text: 'Enter quantity (integer)'
                        multiline: False
                        size_hint_y: None
                        height: 44
                        on_text: root.update_reduced_price()
                    Label:
                        text: 'Reduced price: ' + root.reduced_price
                        size_hint_y: None
                        height: 24
                    Button:
                        text: 'Waste'
                        size_hint_y: None
                        height: 48
                        on_press: root.confirm_and_waste_def()
            
                    Label:
                        text: root.message
                        color: (1,0,0,1)
                        size_hint_y: None
                        height: 24
            Screen:
                name: 'qualityWaste'
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10

                    # Back button and title
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Back'
                            size_hint_x: None
                            width: 100
                            on_press: root.show_subscreen('wasteScan')
                        Label:
                            text: 'Quality Waste'
                            font_size: 20
                    
                    # Product information
                    Label:
                        text: 'UPC: ' + root.product_id
                        size_hint_y: None
                        height: 24
                    Label:
                        text: root.product_name
                        size_hint_y: None
                        height: 24
                    Label:
                        text: 'Quantity'
                        size_hint_y: None
                        height: 24
                    
                    # Option to select quantity mode (single or tray)
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Single'
                            on_press: root.select_qty_mode('single')
                            background_color: (0,0,0,1)
                            color: (1,1,1,1)
                        Button:
                            text: 'Tray'
                            on_press: root.select_qty_mode('tray')
                            background_color: (0,0,0,1)
                            color: (1,1,1,1)
                        Label:
                            text: 'Tray: ' + str(root.tray_size)
                        
                    # Input field for quantity
                    TextInput:
                        id: q_qty
                        hint_text: 'Enter quantity (integer)'
                        multiline: False
                        size_hint_y: None
                        height: 44
                    
                    # Option to submit waste
                    Button:
                        text: 'Waste'
                        size_hint_y: None
                        height: 48
                        on_press: root.confirm_and_waste_quality()

                    # Primary action button on qualityWaste - label changes by mode
                    Button:
                        text: 'Update' if root.summary_update_mode else ('Add to Summary' if root.summary_mode else 'Waste')
                        size_hint_y: None
                        height: 48
                        on_press: root.quality_primary_action()


                    # Option to add item to summary list
                    Button:
                        text: 'Add to Summary'
                        size_hint_y: None
                        height: 48
                        on_press: root.add_to_summary_quality()
                    
                    # Error message display
                    Label:
                        text: root.message
                        color: (1,0,0,1)
                        size_hint_y: None
                        height: 24

            Screen:
                name: 'summaryScreen'
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Back'
                            size_hint_x: None
                            width: 100
                            on_press: root.summary_back()
                        Label:
                            text: 'Summary'
                            font_size: 20
                        
                        # Toggles delete/update column
                        Button:
                            text: 'Done' if root.summary_delete_mode else 'Delete'
                            size_hint_x: None
                            width: 100
                            on_press: root.toggle_delete_mode()
                            
                    ScrollView:
                        do_scroll_x: False
                        GridLayout:
                            id: summary_list
                            cols: 1
                            size_hint_y: None
                            height: self.minimum_height
                            row_default_height: 36
                            row_force_default: True
                            spacing: 6
                    BoxLayout:
                        size_hint_y: None
                        height: 48
                        spacing: 10
                        Button:
                            text: 'Scan More' if root.summary_return_to == 'wasteScan' else 'Return'
                            on_press: root.summary_back()
                        Button:
                            text: 'Submit'
                            on_press: root.confirm_submit_summary()

                    
                    # Error message
                    Label:
                        text: root.message
                        color: (1,0,0,1)
                        size_hint_y: None
                        height: 24
                                    


<StockCountScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        ScreenManager:
            id: count_sm
            transition: NoTransition()

            # Single scan mode screen
            Screen:
                name: 'scanSingle'
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10

                        # Title
                        Label:
                            text: 'Stock Counting'
                            font_size: 22
                        
                        # Goes back to menu
                        Button:
                            text: 'Back to Menu'
                            size_hint_x: None
                            width: 140
                            on_press: root.back_to_menu()
                    
                    # Barcode scanning
                    Label:
                        text: 'Scan / Enter UPC'
                        font_size: 24
                        size_hint_y: None
                        height: 44
                    TextInput:
                        id: single_barcode
                        hint_text: 'UPC'
                        multiline: False
                        size_hint_y: None
                        height: 44
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10

                        # Opens scanner
                        Button:
                            text: 'Scan'
                            on_press: root.open_scanner_single()
                        
                        # Continues with scanned barcode
                        Button:
                            text: 'Continue'
                            on_press: root.continue_single()
                    
                    # Option to switch to count multiple products
                    Button:
                        text: 'Scan Multiple Products'
                        size_hint_y: None
                        height: 48
                        on_press: root.start_multi_scan()
                    
                    # Error messages
                    Label:
                        text: root.message
                        color: (1,0,0,1)
                        size_hint_y: None
                        height: 24

            # Product count screen                       
            Screen:
                name: 'counting'
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10

                    # Header bar
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10

                        # Goes back to product scan
                        Button:
                            text: 'Back'
                            size_hint_x: None
                            width: 90
                            on_press: root.back_from_counting()
                        Label:
                            text: 'Stock Counting'   # title
                            font_size: 22
                        Button:
                            text: 'Exit'
                            size_hint_x: None
                            width: 90
                            on_press: root.exit_flow()   # Exits the entire flow

                    # Product X of X- only visible in multi-mode
                    Label:
                        text: ('Product ' + str(root.product_index+1) + ' of ' + str(root.total_products)) if root.multi_mode else ''
                        size_hint_y: None
                        height: 24
                    # Section pills - disabled indicators
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Stock Room'
                            disabled: False
                            background_color: (0,0,0,1) if root.section=='stockroom' else (1,1,1,1)
                            color: (1,1,1,1) if root.section=='stockroom' else (0,0,0,1)
                        Button:
                            text: 'Shop Floor'
                            disabled: False
                            background_color: (0,0,0,1) if root.section=='shopfloor' else (1,1,1,1)
                            color: (1,1,1,1) if root.section=='shopfloor' else (0,0,0,1)
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: 80
                        padding: 10
                        spacing: 5
                        Label:
                            text: 'UPC: ' + root.product_id
                            size_hint_y: None
                            height: 24
                        Label:
                            text: root.product_name
                            size_hint_y: None
                            height: 24
                    TextInput:
                        id: count_qty
                        hint_text: 'Enter Quantity (blank = 0)'
                        multiline: False
                        size_hint_y: None
                        height: 44
  # Single/Tray quantity mode toggle
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        spacing: 10
                        Button:
                            text: 'Single'
                            on_press: root.select_qty_mode('single')
                            background_color: (0,0,0,1) if root.qty_mode=='single' else (1,1,1,1)
                            color: (1,1,1,1) if root.qty_mode=='single' else (0,0,0,1)
                        Button:
                            text: 'Tray'
                            on_press: root.select_qty_mode('tray')
                            background_color: (0,0,0,1) if root.qty_mode=='tray' else (1,1,1,1)
                            color: (1,1,1,1) if root.qty_mode=='tray' else (0,0,0,1)
                        Label:
                            text: 'Tray: ' + str(root.tray_size)

                    # Primary button - label adapts to mode, section, and position
                    Button:
                        text: 'Next Section' if (not root.multi_mode and root.section=='stockroom') else ('Finish' if (not root.multi_mode and root.section=='shopfloor') else ('Submit' if (root.multi_mode and root.section=='shopfloor' and root.product_index==root.total_products-1) else 'Next'))
                        on_press: root.next_section_single() if not root.multi_mode else root.next_product()
                    # Skip button - hidden on last shopfloor product
                    Button:
                        text: 'Skip to next section' if (root.multi_mode and root.section=='stockroom') else 'Skip and submit'
                        opacity: 1 if (root.multi_mode and (root.section=='stockroom' or (root.section=='shopfloor' and root.product_index < root.total_products-1))) else 0
                        disabled: False if (root.multi_mode and (root.section=='stockroom' or (root.section=='shopfloor' and root.product_index < root.total_products-1))) else True
                        on_press: root.skip_to_next_section()

                    # Error label
                    Label:
                        text: root.message
                        color: (1,0,0,1)
                        size_hint_y: None
                        height: 24

            # Multiple product scan screen                      
            Screen:
                name: 'scanMulti'
                BoxLayout:
                    orientation: 'vertical'
                    spacing: 10

                    # Top header
                    BoxLayout:
                        size_hint_y: None
                        height: 44
                        Button:
                            text: 'Back'
                            size_hint_x: None
                            width: 90
                            on_press: root.back_to_scan_single()
                        Label:
                            text: 'Stock Counting'
                            font_size: 22
                    
                    # Prompts user to scan their next product
                    Label:
                        text: 'Scan Next Product'
                        font_size: 26
                        size_hint_y: None
                        height: 44

                    # Barcode input
                    Button:
                        text: 'Scan barcode'
                        size_hint_y: None
                        height: 44
                        on_press: root.open_scanner_multi()
                    TextInput:
                        id: multi_barcode
                        hint_text: 'or enter UPC'
                        multiline: False
                        size_hint_y: None
                        height: 44
                        on_text_validate: root.add_scanned_from_multi_input()

                    # Recently scanned info box
                    BoxLayout:  
                        orientation: 'vertical'
                        size_hint_y: None
                        height: 90
                        Label:
                            text: 'Recently Scanned:'
                        Label:
                            text: 'UPC: ' + root.recently_scanned_id
                        Label:
                            text: root.recently_scanned_name
                    
                    # Header for queued products list
                    Label:
                        text: 'Products to be scanned'
                        size_hint_y: None
                        height: 24
                    
                    # Scrollable list of products queued
                    ScrollView:
                        do_scroll_x: False
                        GridLayout:
                            id: multi_list
                            cols: 1
                            size_hint_y: None
                            height: self.minimum_height
                            row_default_height: 44
                            row_force_default: True
                            spacing: 6

                    # Proceeds to the counting screen once all products added
                    Button:
                        text: 'Continue'
                        size_hint_y: None
                        height: 48
                        on_press: root.continue_multi_to_counting()
                    
"""
class StoreApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from api import ApiClient
        self.api = ApiClient(base_url='http://127.0.0.1:5000')
    def build(self):
        from kivy.lang import Builder
        sm = Builder.load_string(KV)
        sm.app = self
        sm.current = "login"
        return sm

if __name__ == '__main__':
    StoreApp().run()
