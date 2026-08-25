
from .base import Widget

class TalkBack:
    enabled = False
    
    @staticmethod
    def speak(text):
        if TalkBack.enabled:
            print(f"Speaking: {text}")

class HighContrastMode:
    enabled = False

class LargeTextMode:
    enabled = False

class ScreenReader(Widget):
    pass
