
from .base import Widget
from renderer.colors import Palette, Color
from .label import Label
from .text_input import TextInput
from .layouts import VerticalLayout, HorizontalLayout
import math

class WebView(Widget):
    def __init__(self, url="about:blank", **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.background_color = Palette.WHITE
    
    def draw(self, canvas):
        super().draw(canvas)
        canvas.draw_text(f"WebView: {self.url}", self.x + 10, self.y + 10, Palette.BLACK)

class MapView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Color(200, 230, 255) # Water color
    
    def draw(self, canvas):
        super().draw(canvas)
        # Draw some "roads"
        canvas.draw_rect(self.x + 50, self.y, 20, self.height, Palette.WHITE, filled=True)
        canvas.draw_rect(self.x, self.y + 100, self.width, 20, Palette.WHITE, filled=True)
        canvas.draw_text("Map Data © OpenStreetMap", self.x + 5, self.y + self.height - 20, Palette.BLACK, size=10)

class ChartView(Widget):
    def __init__(self, data=[], type="bar", **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.type = type
        
    def draw(self, canvas):
        if not self.data:
            canvas.draw_text("No Data", self.x, self.y, Palette.GRAY_500)
            return
            
        if self.type == "bar":
            max_val = max(self.data)
            bar_width = self.width / len(self.data)
            for i, val in enumerate(self.data):
                h = (val / max_val) * (self.height - 20)
                x = self.x + i * bar_width
                y = self.y + self.height - h
                canvas.draw_rect(x + 2, y, bar_width - 4, h, Palette.PRIMARY, filled=True)
        # Line and Pie omitted for brevity but structure is here

class CalendarView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.SURFACE
        
    def draw(self, canvas):
        super().draw(canvas)
        # Header
        canvas.draw_text("October 2023", self.x + 10, self.y + 10, Palette.BLACK, size=16)
        # Grid
        cell_w = self.width // 7
        cell_h = (self.height - 40) // 5
        for i in range(31):
            r = i // 7
            c = i % 7
            canvas.draw_text(str(i+1), self.x + c*cell_w + 10, self.y + 40 + r*cell_h + 10, Palette.GRAY_900)

class QRCodeScanner(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.BLACK
    
    def draw(self, canvas):
        super().draw(canvas)
        # Draw scanner frame
        cx, cy = self.x + self.width//2, self.y + self.height//2
        size = 100
        canvas.draw_rect(cx - size, cy - size, size*2, size*2, Palette.ACCENT, filled=False) # Border only
        canvas.draw_text("Scan QR Code", cx - 40, cy + size + 20, Palette.WHITE)

class BarcodeScanner(QRCodeScanner):
    pass

class PDFView(Widget):
    def __init__(self, filename="", **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.background_color = Palette.GRAY_200
        
    def draw(self, canvas):
        super().draw(canvas)
        canvas.draw_text(f"PDF: {self.filename}", self.x + 10, self.y + 10, Palette.BLACK)

class RichTextView(Label):
    pass # Extend Label with parsing logic in future

class CodeEditor(TextInput):
    def draw(self, canvas):
        # Draw line numbers gutter
        gutter_w = 30
        canvas.draw_rect(self.x, self.y, gutter_w, self.height, Palette.GRAY_200, filled=True)
        # Call super draw with offset (would need modify TextInput to support offset or padding)
        super().draw(canvas)

class TerminalView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.BLACK
        self.lines = ["> System initialized...", "> Ready."]
        
    def draw(self, canvas):
        super().draw(canvas)
        y_off = 10
        for line in self.lines:
            canvas.draw_text(line, self.x + 10, self.y + y_off, Palette.GREEN, font_name="Roboto-Mono.ttf", size=14)
            y_off += 20
