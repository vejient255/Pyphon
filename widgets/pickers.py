
from .base import Widget
from .layouts import VerticalLayout, HorizontalLayout
from .label import Label
from .button import Button
from renderer.colors import Palette
import time

class DatePicker(VerticalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Select Date (Inline)", size=14))
        # Calendar Grid
        grid = VerticalLayout(height=200)
        # Mock rows
        grid.add_widget(Label(text="Su Mo Tu We Th Fr Sa"))
        self.add_widget(grid)

class TimePicker(HorizontalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="12", size=24))
        self.add_widget(Label(text=":", size=24))
        self.add_widget(Label(text="00", size=24))

class DateTimePicker(VerticalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(DatePicker())
        self.add_widget(TimePicker())

class CountdownTimer(Label):
    def __init__(self, seconds=60, **kwargs):
        super().__init__(text=str(seconds), **kwargs)
        self.seconds = seconds
        self.running = False
    
    def start(self):
        self.running = True
        # Need loop/update mechanism in main app loop or use time delta in draw

    def draw(self, canvas):
        if self.running and self.seconds > 0:
            # Simple decrement hack for visual only (not accurate timing)
            # In real app, use delta time passed
            pass 
        super().draw(canvas)

class Stopwatch(Label):
    def __init__(self, **kwargs):
        super().__init__(text="00:00:00", **kwargs)
        self.start_time = 0
        self.running = False

    def start(self):
        self.start_time = time.time()
        self.running = True
        
    def draw(self, canvas):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            m, s = divmod(elapsed, 60)
            h, m = divmod(m, 60)
            self.text = f"{h:02d}:{m:02d}:{s:02d}"
        super().draw(canvas)

class TimeRangePicker(HorizontalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Start: 09:00"))
        self.add_widget(Label(text="-"))
        self.add_widget(Label(text="End: 17:00"))
