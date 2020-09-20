from datetime import timedelta, datetime

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from tools.db import run_query
from tools.timeutils import get_today_time


class ClockWidget(MDScreen):
    clock = StringProperty()

    def __init__(self, **kwargs):
        super(ClockWidget, self).__init__(**kwargs)
        self.seconds = 0
        self.start_time = None
        self._saved_seconds = timedelta(seconds=get_today_time())
        work_hours = MDApp.get_running_app().settings.get('work_hours')
        work_hours = timedelta(hours=work_hours)
        self.clock = ("-" if self._saved_seconds < work_hours else "") + str(
            work_hours - self._saved_seconds
        ) if self._saved_seconds.seconds != 0 else "START"
        self.running = False
        Clock.schedule_interval(self.new_day, 60)

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

    def update(self, *args):
        delta = datetime.now() - self.start_time
        self.seconds = delta - timedelta(microseconds=delta.microseconds)
        self.seconds += self._saved_seconds
        work_hours = MDApp.get_running_app().settings.get('work_hours')
        if self.seconds < timedelta(
                hours=work_hours):
            self.clock = "-%s" % str(
                timedelta(hours=work_hours) - self.seconds)
        else:
            self.clock = str(self.seconds - timedelta(hours=8))

        if self.start_time.strftime("%Y-%m-%d") != datetime.now().strftime(
                "%Y-%m-%d"):
            self.stop()
            self.start()

    def new_day(self, *args):
        if self.start_time.day < datetime.now().day:
            work_hours = MDApp.get_running_app().settings.get('work_hours')
            self.clock = "-%s:00:00" % work_hours

    def on_exit(self):
        Clock.unschedule(self.new_day)
        self.stop()
