from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList

from widgets.clock_widget import ClockWidget
from widgets.settings import SettingsWidget


class ContentNavigationDrawer(BoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


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
