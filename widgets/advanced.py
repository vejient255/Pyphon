
from .base import Widget
from renderer.colors import Palette

class ARView(Widget):
    def draw(self, canvas):
        super().draw(canvas)
        canvas.draw_text("AR View (Camera + Overlay)", self.x, self.y, Palette.WHITE)

class VRView(Widget):
    def draw(self, canvas):
        super().draw(canvas)
        # Split screen L/R
        w2 = self.width // 2
        canvas.draw_rect(self.x, self.y, w2, self.height, Palette.BLACK, filled=True)
        canvas.draw_rect(self.x + w2, self.y, w2, self.height, Palette.BLACK, filled=True)

class Object3DView(Widget):
    pass

class NeumorphicWidget(Widget):
    def draw(self, canvas):
        # Light and dark shadows
        canvas.draw_rect(self.x, self.y, self.width, self.height, Palette.SURFACE, filled=True)
        # Emulate shadows (simple)

class GlassmorphismPanel(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.Color(255, 255, 255, 50) # Semi-transparent
        
    def draw(self, canvas):
        canvas.draw_rect(self.x, self.y, self.width, self.height, self.background_color, filled=True)
        # Blur not easily possible in SDL2 without shaders, assuming simple alpha

class DynamicIsland(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.BLACK
        self.border_radius = 20
        self.width = 120
        self.height = 35
        self.expanded = False
        
    def expand(self):
        self.width = 300
        self.height = 100
        self.expanded = True
