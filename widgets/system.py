
from .base import Widget
from renderer.colors import Palette

class Keyboard(Widget):
    # Virtual Keyboard UI
    def draw(self, canvas):
        super().draw(canvas)
        canvas.draw_rect(self.x, self.y, self.width, self.height, Palette.GRAY_200, filled=True)
        canvas.draw_text("Q W E R T Y U I O P", self.x + 10, self.y + 10, Palette.BLACK)

class MouseCursor(Widget):
    pass

class Touchpad(Widget):
    pass

class GestureDetector(Widget):
    pass

class VibrationFeedback:
    @staticmethod
    def vibrate(ms=100):
        print(f"*Vibrate {ms}ms*")

class QuickSettingsTile(Widget):
    pass

class AppShortcut(Widget):
    pass

class PictureInPicture(Widget):
    pass

class SplitScreen(Widget):
    pass

class EdgePanel(Widget):
    pass
