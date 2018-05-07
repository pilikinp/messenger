from kivy.app import App
from screens.screenmanager import sm, screens
from kivy.uix.screenmanager import ScreenManagerException
from kivymd.theming import ThemeManager
# from chat.chat import Chat



from kivy.config import  Config
Config.set('graphics', 'width', '50')
Config.set('graphics', 'height', '512')

class PyMessenger(App):
    title = 'PyMessenger'

    screen_manager = None
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Grey'


    def initialize_app(self):

        self.screen_manager = sm
        self.switch_screen('main')

    def switch_screen(self, screen_name):
        if screen_name in screens.keys():
            screen = screens[screen_name](name=screen_name)
            self.screen_manager.switch_to(screen)
        else:
            raise ScreenManagerException('Error')

    def build(self):
        self.initialize_app()
        return self.screen_manager

if __name__ == '__main__':
    PyMessenger().run()
