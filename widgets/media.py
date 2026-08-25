
from .base import Widget
from renderer.colors import Palette, Color
from .label import Label
from .button import Button
from .slider import Slider
from .layouts import VerticalLayout, HorizontalLayout
import sdl2
import math
import random

class ImageView(Widget):
    def __init__(self, source=None, scale_type="fit", **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.scale_type = scale_type
    
    def draw(self, canvas):
        if not self.visible or not self.source:
            return
        
        # Draw placeholder if image loading fails or not implemented fully
        # Assuming canvas.draw_image handles logic
        canvas.draw_image(self.source, self.x, self.y, self.width, self.height)

class VideoView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_playing = False
        self.background_color = Palette.BLACK
        
    def draw(self, canvas):
        super().draw(canvas)
        # Draw Play icon in center
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        if not self.is_playing:
            # Triangle
            canvas.draw_text("▶", cx - 10, cy - 10, Palette.WHITE, size=30)
        else:
            canvas.draw_text("Playing...", cx - 30, cy - 10, Palette.WHITE, size=16)

class AudioPlayer(VerticalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 10
        self.background_color = Palette.SURFACE
        
        # Info
        self.add_widget(Label(text="Song Title", size=16, color=Palette.BLACK))
        self.add_widget(Label(text="Artist Name", size=12, color=Palette.GRAY_500))
        
        # Controls
        controls = HorizontalLayout(height=40, spacing=10)
        controls.add_widget(Button(text="⏮", width=40))
        self.play_btn = Button(text="▶", width=40)
        controls.add_widget(self.play_btn)
        controls.add_widget(Button(text="⏭", width=40))
        self.add_widget(controls)
        
        # Progress
        self.add_widget(Slider(value=30))

class CameraView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.BLACK
        
    def draw(self, canvas):
        super().draw(canvas)
        canvas.draw_text("CAMERA PREVIEW", self.x + 20, self.y + self.height//2, Palette.WHITE)

class GalleryView(Widget):
    # Grid of images
    def __init__(self, images=[], cols=3, **kwargs):
        super().__init__(**kwargs)
        self.images = images
        self.cols = cols
        
    def draw(self, canvas):
        # Simple grid logic
        cell_w = self.width // self.cols
        cell_h = cell_w
        for i, img in enumerate(self.images):
            r = i // self.cols
            c = i % self.cols
            # Placeholder rects
            canvas.draw_rect(self.x + c*cell_w, self.y + r*cell_h, cell_w-2, cell_h-2, Palette.GRAY_300, filled=True)

class MediaController(HorizontalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = 50
        self.add_widget(Button(text="Play/Pause"))
        self.add_widget(Slider(width=100))

class WaveformView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [random.random() for _ in range(50)]
        self.color = Palette.PRIMARY
        
    def draw(self, canvas):
        if not self.visible:
            return
        
        mid_y = self.y + self.height // 2
        step_x = self.width / len(self.data)
        
        for i, val in enumerate(self.data):
            h = val * (self.height / 2)
            x = self.x + i * step_x
            canvas.draw_rect(x, mid_y - h, step_x - 1, h * 2, self.color, filled=True)
