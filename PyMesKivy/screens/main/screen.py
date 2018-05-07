from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from screens.base.screen import BaseScreen
Builder.load_file('screens/main/main.kv')

class MainScreen(BaseScreen):
    title = 'Login'
    pass