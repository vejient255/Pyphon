# widgets/spinner.py
from .base import Widget
from renderer.colors import Palette, Color

class Spinner(Widget):
    def __init__(self, items=None, selected_index=0, x=0, y=0, width=150, height=48, id=None):
        super().__init__(x, y, width, height, id)
        self.items = items if items else []
        self.selected_index = selected_index
        self.is_open = False
        
        # Estilo Material
        self.background_color = Palette.SURFACE
        self.border_color = Palette.OUTLINE
        self.border_width = 1
        self.border_radius = 4
        self.text_color = Palette.GRAY_900

    def draw(self, canvas):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        
        # Dibujar botón del spinner
        canvas.draw_rounded_rect(abs_x, abs_y, self.width, self.height, self.border_radius, self.background_color)
        canvas.draw_rect(abs_x, abs_y + self.height - 1, self.width, 1, self.border_color) # Borde inferior simple

        # Dibujar texto seleccionado
        if self.items and 0 <= self.selected_index < len(self.items):
            canvas.draw_text(self.items[self.selected_index], abs_x + 12, abs_y + (self.height // 2) - 10, self.text_color, size=18)

        # Dibujar flecha (triángulo simplificado)
        arrow_x = abs_x + self.width - 24
        arrow_y = abs_y + (self.height // 2) - 2
        canvas.draw_rect(arrow_x, arrow_y, 10, 2, self.text_color)
        
        # Si está abierto, dibujar lista desplegable usando el sistema de OVERLAYS de PyPhonOS
        # Esto asegura que el menú aparezca por encima de cualquier otro widget (Z-Index top)
        if self.is_open:
            def draw_spinner_dropdown():
                item_h = 40
                list_h = len(self.items) * item_h
                # Fondo del menú
                canvas.draw_rect(abs_x, abs_y + self.height, self.width, list_h, Palette.SURFACE, alpha=255)
                # Sombra para el desplegable
                canvas.draw_rect(abs_x, abs_y + self.height + list_h, self.width, 2, Color(0,0,0,50))
                
                for i, item in enumerate(self.items):
                    iy = abs_y + self.height + (i * item_h)
                    # Resaltar si es el seleccionado
                    if i == self.selected_index:
                        canvas.draw_rect(abs_x, iy, self.width, item_h, Palette.PRIMARY.darken(0.1), alpha=40)
                    
                    canvas.draw_text(item, abs_x + 12, iy + (item_h // 2) - 10, self.text_color, size=16)
            
            canvas.overlays.append(draw_spinner_dropdown)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False

        from core.app import MobileApp # Importación diferida para evitar ciclos

        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)
        abs_x, abs_y = self.get_absolute_position()

        if etype == "touch_up":
            if self.is_open:
                # 1. Verificar si se hizo clic en un item de la lista (que está en Overlays)
                item_h = 40
                for i in range(len(self.items)):
                    # La lista se dibuja justo debajo del Spinner
                    iy = abs_y + self.height + (i * item_h)
                    if abs_x <= ex <= abs_x + self.width and iy <= ey <= iy + item_h:
                        self.selected_index = i
                        self.is_open = False
                        # Liberamos la prioridad de eventos
                        if MobileApp.INSTANCE:
                            MobileApp.INSTANCE.event_overlay = None
                        self.events.on_change.emit()
                        return True
                
                # 2. Si se hizo clic fuera o se quiere cerrar
                self.is_open = False
                if MobileApp.INSTANCE:
                    MobileApp.INSTANCE.event_overlay = None
                return True
            else:
                # Abrir el menú
                if self.is_point_inside(ex, ey):
                    self.is_open = True
                    # Reclamamos prioridad absoluta de eventos
                    if MobileApp.INSTANCE:
                        MobileApp.INSTANCE.event_overlay = self
                    return True
        
        return False
