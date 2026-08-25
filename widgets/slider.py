# widgets/slider.py
from .base import Widget
from renderer.colors import Palette, Color

class Slider(Widget):
    def __init__(self, value=0, min_val=0, max_val=100, x=0, y=0, width=200, height=32, id=None):
        super().__init__(x, y, width, height, id)
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.is_dragging = False
        
        # Estilo Material
        self.track_color = Palette.GRAY_300
        self.active_track_color = Palette.PRIMARY
        self.thumb_color = Palette.PRIMARY
        self.thumb_radius = 10

    def draw(self, canvas):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        mid_y = abs_y + self.height // 2
        
        # Calcular posición del thumb
        percentage = (self.value - self.min_val) / (self.max_val - self.min_val)
        thumb_x = abs_x + int(percentage * self.width)
        
        # Dibujar track (fondo)
        canvas.draw_rect(abs_x, mid_y - 2, self.width, 4, self.track_color)
        
        # Dibujar track activo
        canvas.draw_rect(abs_x, mid_y - 2, thumb_x - abs_x, 4, self.active_track_color)
        
        # Dibujar thumb (círculo)
        canvas.draw_circle(thumb_x, mid_y, self.thumb_radius, self.thumb_color)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False

        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)
        abs_x, abs_y = self.get_absolute_position()

        if etype == "touch_down":
            if self.is_point_inside(ex, ey):
                self.is_dragging = True
                self._update_value_from_x(ex)
                return True
        
        elif etype == "touch_move" and self.is_dragging:
            self._update_value_from_x(ex)
            return True
            
        elif etype == "touch_up":
            if self.is_dragging:
                self.is_dragging = False
                return True
        
        return False

    def _update_value_from_x(self, ex):
        abs_x, _ = self.get_absolute_position()
        relative_x = max(0, min(ex - abs_x, self.width))
        percentage = relative_x / self.width
        new_val = self.min_val + percentage * (self.max_val - self.min_val)
        
        if new_val != self.value:
            self.value = new_val
            self.events.on_change.emit()
