# widgets/radio_button.py
from .base import Widget
from renderer.colors import Palette, Color

class RadioButton(Widget):
    def __init__(self, checked=False, label="", group=None, x=0, y=0, size=24, id=None):
        super().__init__(x, y, size, size, id)
        self.checked = checked
        self.label = label
        self.group = group
        self.size = size
        
        # Estilo Material
        self.active_color = Palette.PRIMARY
        self.inactive_color = Palette.OUTLINE
        
        if group is not None:
            group.add_button(self)

    def draw(self, canvas):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        center_x = abs_x + self.size // 2
        center_y = abs_y + self.size // 2
        
        # Dibujar círculo exterior
        color = self.active_color if self.checked else self.inactive_color
        canvas.draw_circle(center_x, center_y, self.size // 2, color)
        
        # Círculo interior (blanco para el borde)
        canvas.draw_circle(center_x, center_y, (self.size // 2) - 2, Palette.SURFACE)
        
        # Punto central si está marcado
        if self.checked:
            canvas.draw_circle(center_x, center_y, self.size // 4, self.active_color)

        # Dibujar Label
        if self.label:
            canvas.draw_text(self.label, abs_x + self.size + 10, abs_y + (self.size // 2) - 10, Palette.GRAY_900, size=18)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False

        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == "touch_up":
            total_width = self.size + (len(self.label) * 10 if self.label else 0)
            abs_x, abs_y = self.get_absolute_position()
            
            if abs_x <= ex <= abs_x + total_width and abs_y <= ey <= abs_y + self.size:
                if not self.checked:
                    if self.group:
                        self.group.select(self)
                    else:
                        self.checked = True
                    self.events.on_change.emit()
                    self.events.on_click.emit()
                return True
        
        return False

class RadioGroup:
    def __init__(self):
        self.buttons = []

    def add_button(self, button):
        button.group = self
        self.buttons.append(button)

    def select(self, selected_button):
        for btn in self.buttons:
            btn.checked = (btn == selected_button)
            btn.events.on_change.emit()
