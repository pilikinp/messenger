from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.utils import hex_colormap, get_color_from_hex
from kivy.metrics import dp

KV = """
# Разметка пункта списка.
<Item@BoxLayout>:
    color: []
    name_color: ''

    Label
        canvas.before:
            Color:
                rgba: root.color
            Rectangle:
                pos: self.pos
                size: self.size
        text: root.name_color
        color: 0, 0, 0, 1

# Контейнер для списка.
BoxLayout:
    orientation: "vertical"

    # Используйте вместо ScrollView.
    RecycleView:
        id: rv
        key_size: 'height'
        key_viewclass: 'viewclass'

        RecycleBoxLayout:
            id: box
            default_size: None, None
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(5)

"""

class RecycleViewApp(App):
    def build(self):
        self.root = Builder.load_string(KV)
        self.rv = self.root.ids.rv
        self.create()

    def create(self):
        colors = []

        # Создание списка.
        for name_color in hex_colormap.keys():
            colors.append({
                "name_color": name_color,
                "viewclass": "Item",
                'color': get_color_from_hex(hex_colormap[name_color]),
                'height': dp(40)
            })

        self.rv.data = colors

RecycleViewApp().run()