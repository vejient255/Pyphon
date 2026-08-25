
from .base import Widget
from .layouts import VerticalLayout, HorizontalLayout
from .label import Label
from .button import Button
from renderer.colors import Palette
import os

class FilePicker(VerticalLayout):
    def __init__(self, path=".", **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.add_widget(Label(text=f"Current: {path}"))
        
        file_list = VerticalLayout(height=200) # Should be ScrollView
        try:
            items = os.listdir(path)[:5] # Limit for display
            for item in items:
                file_list.add_widget(Label(text=f"📄 {item}"))
        except:
            pass
        self.add_widget(file_list)

class DirectoryPicker(FilePicker):
    pass

class FileExplorer(FilePicker):
    pass

class StorageInfo(Widget):
    def draw(self, canvas):
        super().draw(canvas)
        canvas.draw_text("Storage: 45% used", self.x, self.y, Palette.GRAY_700)
        # Draw bar
        canvas.draw_rect(self.x, self.y + 20, self.width, 10, Palette.GRAY_300, filled=True)
        canvas.draw_rect(self.x, self.y + 20, self.width * 0.45, 10, Palette.PRIMARY, filled=True)

class BatteryIndicator(Widget):
    def __init__(self, level=85, **kwargs):
        super().__init__(**kwargs)
        self.level = level
        
    def draw(self, canvas):
        # Draw battery icon
        w, h = 40, 20
        canvas.draw_rect(self.x, self.y, w, h, Palette.BLACK, filled=False)
        fill_w = (w - 4) * (self.level / 100)
        canvas.draw_rect(self.x + 2, self.y + 2, fill_w, h - 4, Palette.SUCCESS, filled=True)
        # Tip
        canvas.draw_rect(self.x + w, self.y + 5, 3, 10, Palette.BLACK, filled=True)

class NetworkStatus(Widget):
    def draw(self, canvas):
        # Wifi icon
        canvas.draw_text("WiFi: Connected", self.x, self.y, Palette.BLACK)
