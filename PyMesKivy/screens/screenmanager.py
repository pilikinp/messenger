from kivy.uix.screenmanager import ScreenManager, SlideTransition
from screens.base.screen import BaseScreen
from screens.registration.registration import RegScreen
from screens.main.screen import MainScreen

sm = ScreenManager(transition= SlideTransition())
screens = {
    'main': MainScreen,
    'reg': RegScreen,
}