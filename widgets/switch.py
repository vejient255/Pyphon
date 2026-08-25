# widgets/switch.py
from .base import Widget
from renderer.colors import Palette, Color

class Switch(Widget):
    def __init__(self, x=0, y=0, active=False, on_change=None):
        """
        Widget de Interruptor (Switch) con estética Material 3.
        """
        super().__init__(x, y, width=52, height=32, background_color=None)
        self.active = active
        self.on_change = on_change
        self.border_radius = 16
        
        # Colores M3
        self.track_off = Palette.GRAY_300
        self.track_on = Palette.PRIMARY.brighten(0.3)
        self.thumb_off = Palette.GRAY_700
        self.thumb_on = Palette.PRIMARY
        
        # Animación simple (posición del thumb)
        self.thumb_pos = 16 if active else 4

    def draw(self, canvas):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        
        # 1. Dibujar Track (Fondo del switch)
        track_color = self.track_on if self.active else self.track_off
        self._draw_rounded_rect(canvas, abs_x, abs_y, self.width, self.height, self.border_radius, track_color)
        
        # 2. Dibujar Thumb (Círculo deslizante)
        thumb_color = self.thumb_on if self.active else self.thumb_off
        target_pos = self.width - 24 if self.active else 4
        
        # Suavizado de posición (animación básica por frame)
        if self.thumb_pos < target_pos:
            self.thumb_pos = min(target_pos, self.thumb_pos + 4)
        elif self.thumb_pos > target_pos:
            self.thumb_pos = max(target_pos, self.thumb_pos - 4)
            
        thumb_x = abs_x + self.thumb_pos
        thumb_y = abs_y + 4
        thumb_size = 24
        
        # Dibujar thumb como un rect redondeado (círculo)
        self._draw_rounded_rect(canvas, thumb_x, thumb_y, thumb_size, thumb_size, thumb_size // 2, thumb_color)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False

        ex, ey = event.get('x', 0), event.get('y', 0)
        etype = event.get('type')

        if etype == "touch_up" and self.is_point_inside(ex, ey):
            self.active = not self.active
            if self.on_change:
                self.on_change(self.active)
            self.events.on_click.emit() # También disparamos on_click para compatibilidad
            return True
            
        return False
