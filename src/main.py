from datetime import datetime

from kivy import Logger, Config
from kivy.core.window import Window

from kivymd.app import MDApp

from tools.db import run_query
from tools.files import store
from tools.timeutils import get_not_counted_days, negative_handle
from widgets.navigation import ItemDrawer

Config.set('kivy', 'window_icon', 'assets/icon.png')


class SimpleTimeTrackerApp(MDApp):

    def __init__(self, **kwargs):
        super(SimpleTimeTrackerApp, self).__init__(**kwargs)

        try:
            self.settings = store.get('settings')
        except KeyError:
            self.settings = {"work_hours": 8}
            store.put('settings', **self.settings)

        try:
            self.current_state = store.get('current_state')
        except KeyError:
            self.current_state = {"flex": 0}
            store.put('current_state', **self.current_state)

        run_query(
            query="CREATE TABLE IF NOT EXISTS day_log ("
                  "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "day_field TEXT, seconds INTEGER, counted INTEGER DEFAULT 0)"
        )

        self.today = datetime.now()
        self.update_flex()
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

    def update_flex(self):
        seconds = 0
        for day in get_not_counted_days():
            seconds += day[1] - (
                    self.settings.get('work_hours') * 60 * 60)
            run_query(
                query="UPDATE day_log SET counted=1 "
                      "WHERE id=:id;",
                params={
                    "id": day[0]})

        self.current_state['flex'] += seconds
        flex = negative_handle(self.current_state['flex'])
        Logger.info("New flex: %s", flex)
        store.put('current_state', **self.current_state)

    def is_new_day(self):
        if self.today.day == datetime.now().day:
            return False
        else:
            self.today = datetime.now()
            return True

    def on_exit(self, arg):
        for child in self.root.content_widget.children:
            child.on_exit()


if __name__ == '__main__':
    SimpleTimeTrackerApp().run()
