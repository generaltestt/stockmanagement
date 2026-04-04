from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp

class LoginScreen(Screen):
    message = StringProperty('')
    store_list = []
    selected_store = None

    def on_kv_post(self, base_widget):
        self.load_stores()

    def load_stores(self):
        app = App.get_running_app()
        self.store_list = app.api.get_stores()
        if not self.store_list:
            self.message = 'Could not load stores. Check server is running.'

    def filter_stores(self, text):
        t = text.lower()
        return [s for s in self.store_list
                if t in s['id'].lower() or t in s['name'].lower()]

    def on_store_text(self, text):
        if len(text) < 1:
            return
        matches = self.filter_stores(text)
        if matches:
            Clock.schedule_once(lambda dt: self.open_dropdown(matches), 0)

    def open_dropdown(self, matches):
        dd = DropDown()
        for s in matches:
            label = f"{s['id']} - {s['name']}"
            btn = Button(text=label, size_hint_y=None, height=40)
            btn.bind(on_release=lambda b, s=s: self.select_store(b.text, dd))
            dd.add_widget(btn)
        dd.open(self.ids.store_search)

    def select_store(self, text, dd):
        self.ids.store_search.text = text
        dd.dismiss()

    def check_store(self):
        store_text = self.ids.store_search.text.strip()
        if not store_text:
            self.message = 'Please enter a store name or ID'
            return
        # extract just the ID from the dropdown format "0725 - Islington"
        store_id = store_text.split(' - ')[0].strip()
        app = App.get_running_app()
        # call the backend to validate the store ID exists in the database
        result = app.api.validate_store(store_id)
        if not result:
            # store not found - show error and stay on the store section
            self.message = 'Store not found'
            return
        self.message = ''
        self.selected_store = result  # save the validated store dict for use in login
        self.show_login_form()        # hide store section and reveal login form

    def show_login_form(self):
        self.ids.store_section.opacity = 0
        self.ids.store_section.disabled = True
        self.ids.store_section.height = 0
        self.ids.login_section.opacity = 1
        self.ids.login_section.disabled = False
        self.ids.store_label.text = self.selected_store['name']

    def do_login(self):
        # Gets username and password inputs
        username = self.ids.username.text.strip()
        password = self.ids.password.text

        # Validates inputs
        if not username or not password:
            self.message = 'Please enter your ID and password'
            return

        # Checks credentials with API
        app = App.get_running_app()
        result = app.api.login(username, password, self.selected_store['id'])

        if result is True:
            self.manager.current = 'menu' # Shows menu if successful
        elif result is False:
            # Error message if wrong ID/password
            self.message = 'Login failed. Check your ID and password.'
        else:
            # Error message if server down
            self.message = 'Could not connect to server. Try again.'


    def back_to_store_login(self):
        # Clears all fields and returns to the store selection screen

        # Resets inputs
        self.ids.username.text = ''
        self.ids.password.text = ''
        self.message = ''  # clear any error message
        self.ids.store_search.text = ''  # resets the store field 

        # Hides login section and shows store section
        self.ids.login_section.opacity = 0
        self.ids.login_section.disabled = True
        self.ids.store_section.opacity = 1
        self.ids.store_section.disabled = False
        self.ids.store_section.height = dp(200)  # restore collapsed height

        
        