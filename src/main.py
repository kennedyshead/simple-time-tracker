from kivy.core.window import Window

from kivymd.app import MDApp

from tools.db import run_query
from tools.files import store
from widgets.navigation import ItemDrawer


class SimpleTimeTrackerApp(MDApp):

    def __init__(self, **kwargs):
        super(SimpleTimeTrackerApp, self).__init__(**kwargs)
        try:
            self.settings = store.get('settings')
        except KeyError:
            self.settings = {"work_hours": 8}
            store.put('settings', **self.settings)
        run_query(
            query="CREATE TABLE IF NOT EXISTS day_log ("
                  "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "day_field TEXT, seconds INTEGER)")
        Window.bind(on_request_close=self.on_exit)

    def build(self):
        self.icon = 'assets/icon.png'
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.primary_hue = "900"

    def on_start(self):
        icons_item = {
            "account-clock-outline": "Log time",
            "account-cog-outline": "Settings"
        }
        for icon_name in icons_item.keys():
            self.root.ids.content_drawer.ids.md_list.add_widget(
                ItemDrawer(icon=icon_name, text=icons_item[icon_name])
            )

    def on_exit(self, arg):
        for child in self.root.content_widget.children:
            child.on_exit()


if __name__ == '__main__':
    SimpleTimeTrackerApp().run()
