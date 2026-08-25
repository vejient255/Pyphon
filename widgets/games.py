
from .base import Widget
from renderer.colors import Palette, Color
from .label import Label
import math

class Joystick(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stick_x = 0
        self.stick_y = 0
        self.active = False
        
    def draw(self, canvas):
        cx, cy = self.x + self.width//2, self.y + self.height//2
        r = min(self.width, self.height) // 2
        
        # Base
        canvas.draw_circle(cx, cy, r, Palette.GRAY_300, alpha=100)
        
        # Stick
        stick_cx = cx + self.stick_x
        stick_cy = cy + self.stick_y
        canvas.draw_circle(stick_cx, stick_cy, r//3, Palette.PRIMARY)
        
    def handle_event(self, event):
        if event['type'] == 'touch_down':
            self.active = True
        elif event['type'] == 'touch_up':
            self.active = False
            self.stick_x = 0
            self.stick_y = 0
        elif event['type'] == 'touch_move' and self.active:
            # Logic to clamp stick inside circle
            pass
        return True

class GamepadView(Widget):
    def draw(self, canvas):
        super().draw(canvas)
        canvas.draw_text("GAMEPAD", self.x, self.y, Palette.BLACK)

class Scoreboard(Widget):
    def __init__(self, score=0, **kwargs):
        super().__init__(**kwargs)
        self.score = score
        
    def draw(self, canvas):
        canvas.draw_text(f"SCORE: {self.score}", self.x, self.y, Palette.ACCENT, size=24)

class AchievementBadge(Widget):
    def __init__(self, title="Winner", **kwargs):
        super().__init__(**kwargs)
        self.title = title
    
    def draw(self, canvas):
        canvas.draw_circle(self.x + 20, self.y + 20, 20, Palette.WARNING)
        canvas.draw_text("🏆", self.x + 10, self.y + 10, Palette.BLACK)

class Leaderboard(Widget):
    pass
