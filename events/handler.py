# PyPhonOS - handler.py
# events/handler.py
from .signals import Signal

class EventHandler:
    def __init__(self):
        """Contenedor de señales estándar para widgets de PyPhonOS."""
        self.on_click = Signal()
        self.on_press = Signal()
        self.on_release = Signal()
        self.on_change = Signal() # Para inputs, sliders, etc.
        self.on_focus = Signal()
        self.on_blur = Signal()
        self.on_key_down = Signal()
        self.on_text_input = Signal()