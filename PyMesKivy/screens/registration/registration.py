from kivy.lang import Builder
from screens.base.screen import BaseScreen
from kivy.uix.screenmanager import Screen


Builder.load_file('screens/registration/registration.kv')

class RegScreen(BaseScreen):
    title = 'Registration'
    def __init__(self, *args, **kwargs):
        super(RegScreen, self).__init__()


    def on_title_press(self, *args):
        pass
