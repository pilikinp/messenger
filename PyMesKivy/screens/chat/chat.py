from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from screens.base.screen import BaseScreen
from kivy.uix.screenmanager import Screen
Builder.load_file('screens/chat/chat.kv')

class MainScreen(Screen):
    title = 'PyMessenger'
    pass