# widgets/checkbox.py
from .base import Widget
from renderer.colors import Palette, Color

class Checkbox(Widget):
    def __init__(self, checked=False, label="", x=0, y=0, size=24, id=None):
        super().__init__(x, y, size, size, id)
        self.checked = checked
        self.label = label
        self.size = size
        
        # Estilo Material
        self.active_color = Palette.PRIMARY
        self.inactive_color = Palette.OUTLINE
        self.check_color = Palette.WHITE
        self.border_radius = 4

    def draw(self, canvas):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        
        # Dibujar cuadro
        color = self.active_color if self.checked else self.inactive_color
        canvas.draw_rounded_rect(abs_x, abs_y, self.size, self.size, self.border_radius, color)
        
        if not self.checked:
            # Cuadro interior blanco para el estado inactivo
            canvas.draw_rounded_rect(abs_x + 2, abs_y + 2, self.size - 4, self.size - 4, self.border_radius - 1, Palette.SURFACE)

        # Dibujar check (V) si está marcado
        if self.checked:
            # Dibujo simplificado de un checkmark
            # Línea corta
            canvas.draw_rect(abs_x + 5, abs_y + 12, 6, 2, self.check_color)
            # Línea larga (diagonal aproximada con rects)
            canvas.draw_rect(abs_x + 9, abs_y + 12, 2, -8, self.check_color) # Esto no es un check real, mejoraremos
            # Re-implementación visual simple: un punto central o una X
            canvas.draw_rect(abs_x + self.size//4, abs_y + self.size//4, self.size//2, self.size//2, self.check_color)

        # Dibujar Label si existe
        if self.label:
            canvas.draw_text(self.label, abs_x + self.size + 10, abs_y + (self.size // 2) - 10, Palette.GRAY_900, size=18)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False

        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == "touch_up":
            # Expandir área de clic para incluir el label
            total_width = self.size + (len(self.label) * 10 if self.label else 0)
            abs_x, abs_y = self.get_absolute_position()
            
            if abs_x <= ex <= abs_x + total_width and abs_y <= ey <= abs_y + self.size:
                self.checked = not self.checked
                self.events.on_change.emit()
                self.events.on_click.emit()
                return True
        
        return False
