from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

# Shared camera screen - reused by waste, stock count, gap scan etc.
# Camera only runs while this screen is visible.
class CameraScanScreen(Screen):

    def on_pre_enter(self):
        # start camera just before transition - feed is ready on arrival
        self.ids.zbarcam.start()

    def on_leave(self):
        # stop camera immediately - releases hardware back to Android
        self.ids.zbarcam.stop()

    def on_code_scanned(self, *args):
        # fires on every ZBarCam frame - most frames return empty symbols
        symbols = self.ids.zbarcam.symbols
        if not symbols:
            return
        code = symbols[0].data.decode('utf-8')  # bytes -> str
        Clock.schedule_once(lambda dt: self.go_back(code), 0.05)

    def go_back(self, code=None):
        """Return to originating screen. code=None = cancelled."""
        sm = self.manager
        back_to = getattr(sm, 'scan_target_screen', 'scan')
        if code is not None:
            scr = sm.get_screen(back_to)
            if hasattr(scr, 'set_barcode'):
                scr.set_barcode(code)
            else:
                target_input = getattr(sm, 'scan_target_input', None)
                if target_input and target_input in scr.ids:
                    scr.ids[target_input].text = code
        sm.current = back_to  # always navigate back
