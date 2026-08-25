# widgets/button.py
from .base import Widget
from renderer.colors import Palette
import sdl2.sdlttf
import sdl2

class Button(Widget):
    def __init__(self, text="Button", x=0, y=0, width=150, height=50, color=None, on_click=None, id=None):
        """
        Widget de botón moderno con estética Material 3.
        """
        super().__init__(x, y, width, height, id, on_click=on_click)
        
        self.text = text
        self.normal_color = color if color else Palette.PRIMARY
        self.pressed_color = self.normal_color.darken(0.15)
        self.text_color = Palette.ON_PRIMARY
        self.is_pressed = False
        
        # Estética Material 3: Esquinas muy redondeadas (o totalmente circulares)
        self.border_radius = 20 
        
        # Elevación (Sombra)
        self.shadow_blur = 6
        self.shadow_offset = (0, 3)

    def draw(self, canvas):
        """Renderiza el botón con el sistema de dibujo de la clase base."""
        if not self.visible:
            return

        # Actualizar color según estado
        self.background_color = self.pressed_color if self.is_pressed else self.normal_color
        
        # Dibujar base (fondo y sombra) usando la implementación de Widget
        super().draw(canvas)

        # Dibujar el texto centrado
        if self.text:
            abs_x, abs_y = self.get_absolute_position()
            text_size = 18
            nombre_archivo_fuente = "Roboto-Medium.ttf" # Fuente más moderna
            
            # Medir texto (usando caché de canvas si es posible)
            font_path = canvas.get_asset_path(f"assets/fonts/{nombre_archivo_fuente}")
            font_key = f"{font_path}_{text_size}"
            
            if font_key not in canvas._font_cache:
                import os
                if os.path.exists(font_path):
                    canvas._font_cache[font_key] = sdl2.sdlttf.TTF_OpenFont(font_path.encode('utf-8'), text_size)

            if font_key in canvas._font_cache:
                font = canvas._font_cache[font_key]
                w, h = sdl2.c_int(), sdl2.c_int()
                sdl2.sdlttf.TTF_SizeUTF8(font, str(self.text).encode('utf-8'), w, h)
                
                text_x = abs_x + (self.width // 2) - (w.value // 2)
                text_y = abs_y + (self.height // 2) - (h.value // 2)
                
                canvas.draw_text(
                    str(self.text), 
                    int(text_x), 
                    int(text_y), 
                    self.text_color, 
                    size=text_size, 
                    font_name=nombre_archivo_fuente
                )

    def handle_event(self, event):
        """Maneja la lógica de clic específica del botón."""
        if not self.enabled or not self.visible:
            return False

        ex, ey = event.get('x', 0), event.get('y', 0)
        etype = event.get('type')
        inside = self.is_point_inside(ex, ey)

        if etype == "touch_down" and inside:
            self.is_pressed = True
            return True
            
        elif etype == "touch_up":
            if self.is_pressed and inside:
                self.is_pressed = False
                # Disparar la señal de clic
                self.events.on_click.emit()
                return True
            self.is_pressed = False
            
        return False