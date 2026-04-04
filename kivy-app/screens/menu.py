from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from datetime import datetime

class MenuScreen(Screen):
    welcome_text = StringProperty("Welcome")
    today_text = StringProperty("")
    show_store_features = BooleanProperty(True)
    can_manage_users = BooleanProperty(False)

    def menuLookup(self):
        self.manager.current = "scan"
    
    def menuWaste(self):
        self.manager.current = "waste"
    
    def menuCount(self):
        self.manager.current = "stock_count" # correct name

    def on_pre_enter(self):
        app = self.manager.app
        fn = (app.api.user or {}).get("first_name", "")
        user = app.api.user or {}
        self.welcome_text = f"Welcome, {fn}!" if fn else "Welcome"
        self.today_text = datetime.now().strftime("%#d %b")  # Windows
        self.show_store_features = (app.api.store_id != "HO")
        self.can_manage_users = (
            user.get("is_head_office", False)
            or user.get("is_admin", False)
        )
