import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from kivy import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.storage.dictstore import DictStore
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty

from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, MDList
from kivymd.uix.screen import MDScreen

file_path = Path('.')

if platform == 'macosx':
    file_path = Path(
        '~/Library/Application Support/%s' % __name__).expanduser()
    file_path.mkdir(parents=True, exist_ok=True)

db = sqlite3.connect(file_path.joinpath('storage.db'))
store = DictStore(file_path.joinpath('settings.json'))

KV = '''
# Menu item in the DrawerList list.
<ItemDrawer>:
    theme_text_color: "Custom"
    on_release: self.parent.navigate_to(self)

    IconLeftWidget:
        id: icon
        icon: root.icon
        theme_text_color: "Custom"
        text_color: root.text_color


<ContentNavigationDrawer>:
    orientation: "vertical"
    padding: "8dp"
    spacing: "8dp"

    AnchorLayout:
        anchor_x: "left"
        size_hint_y: None
        height: avatar.height

        Image:
            id: avatar
            size_hint: None, None
            size: "56dp", "56dp"
            source: "assets/icon.png"

    MDLabel:
        text: "Simple Time Tracker"
        font_style: "Button"
        size_hint_y: None
        height: self.texture_size[1]

    ScrollView:

        DrawerList:
            id: md_list


Screen:
    content_widget: content

    NavigationLayout:

        ScreenManager:

            Screen:

                BoxLayout:
                    orientation: 'vertical'

                    MDToolbar:
                        title: "Simple Time tracker"
                        elevation: 10
                        left_action_items: [['menu', lambda x: nav_drawer.set_state("open")]]

                    BoxLayout:
                        id: content
                    
                        ClockWidget:
                            padding: 0, 50, 0, 0
                            orientation: 'vertical'
                            
                            MDRectangleFlatButton:
                                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                id: toggle
                                text: self.parent.clock
                                on_release: self.parent.toggle()
                                

        MDNavigationDrawer:
            id: nav_drawer

            ContentNavigationDrawer:
                id: content_drawer
    
'''


def run_query(**kwargs):
    cursor = db.cursor()
    cursor.execute(kwargs['query'], kwargs.get('params', {}))
    db.commit()
    cursor.close()


class ContentNavigationDrawer(BoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


def get_today_time():
    cursor = db.cursor()
    cursor.execute(
        "SELECT seconds FROM day_log WHERE day_field=:today", {
            "today": datetime.now().strftime("%Y-%m-%d")})
    seconds = cursor.fetchone()
    return seconds[0] if seconds else 0


class ClockWidget(MDScreen):
    clock = StringProperty()

    def __init__(self, **kwargs):
        super(ClockWidget, self).__init__(**kwargs)
        self.seconds = 0
        self.start_time = None
        self._saved_seconds = timedelta(seconds=get_today_time())
        workhours = MDApp.get_running_app().settings.get('workhours')
        workhours = timedelta(hours=workhours)
        self.clock = ("-" if self._saved_seconds < workhours else "") + str(
            workhours - self._saved_seconds
        ) if self._saved_seconds.seconds != 0 else "START"
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = datetime.now()
            Clock.schedule_interval(self.update, 0.1)

    def stop(self):
        if self.running:
            self.running = False
            delta = datetime.now() - self.start_time
            if self._saved_seconds.seconds == 0:
                self._saved_seconds = delta - timedelta(
                    microseconds=delta.microseconds)
                run_query(
                    query="INSERT INTO day_log (day_field, seconds)"
                          "VALUES (:today, :seconds);",
                    params={
                        "today": self.start_time.strftime("%Y-%m-%d"),
                        "seconds": self._saved_seconds.seconds})
            else:
                self._saved_seconds += delta - timedelta(
                    microseconds=delta.microseconds)
                run_query(
                    query="UPDATE day_log SET seconds=:seconds "
                          "WHERE day_field=:today;",
                    params={
                        "seconds": self._saved_seconds.seconds,
                        "today": datetime.now().strftime("%Y-%m-%d")})

            Clock.unschedule(self.update)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def update(self, *kwargs):
        delta = datetime.now() - self.start_time
        self.seconds = delta - timedelta(microseconds=delta.microseconds)
        self.seconds += self._saved_seconds
        workhours = MDApp.get_running_app().settings.get('workhours')
        if self.seconds < timedelta(
                hours=workhours):
            self.clock = "-%s" % str(
                timedelta(hours=workhours) - self.seconds)
        else:
            self.clock = str(self.seconds - timedelta(hours=8))

        if self.start_time.strftime("%Y-%m-%d") != datetime.now().strftime(
                "%Y-%m-%d"):
            self.stop()
            self.start()

    def on_exit(self):
        self.stop()


class SettingsWidget(MDLabel):
    text = 'Settings'

    def on_exit(self):
        pass


class DrawerList(ThemableBehavior, MDList):

    def navigate_to(self, instance_item):
        self.set_color_item(instance_item)
        content = MDApp.get_running_app().root.content_widget
        content.clear_widgets()
        if instance_item.icon == 'account-clock-outline':
            content.add_widget(ClockWidget())
        if instance_item.icon == 'account-cog-outline':
            content.add_widget(SettingsWidget())

    def set_color_item(self, instance_item):
        """Called when tap on a menu item."""

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color


class SimpleTimeTrackerApp(MDApp):

    def __init__(self, **kwargs):
        super(SimpleTimeTrackerApp, self).__init__(**kwargs)
        try:
            self.settings = store.get('settings')
        except KeyError:
            self.settings = {"workhours": 8}
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
        return Builder.load_string(KV)

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
        pass  # self.root.content.current.on_exit()


if __name__ == '__main__':
    SimpleTimeTrackerApp().run()
