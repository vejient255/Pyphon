# widgets/text_input.py
import sdl2
import time
from .base import Widget
from renderer.colors import Palette, Color

class TextInput(Widget):
    def __init__(self, text="", placeholder="Escribe aquí...", x=0, y=0, width=200, height=48, id=None):
        super().__init__(x, y, width, height, id)
        self.text = text
        self.placeholder = placeholder
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()
        self.cursor_pos = len(text)
        
        # Estilo Material Design
        self.background_color = Palette.SURFACE
        self.border_color = Palette.PRIMARY
        self.border_width = 2
        self.border_radius = 4
        self.text_color = Palette.GRAY_900
        self.placeholder_color = Palette.GRAY_500
        
        self.is_focused = False

    def draw(self, canvas):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        
        # Dibujar fondo y borde
        current_border_color = self.border_color if self.is_focused else Palette.OUTLINE
        current_border_width = self.border_width if self.is_focused else 1
        
        # Dibujar fondo con sombra si está enfocado
        if self.is_focused:
            self.shadow_blur = 4
        else:
            self.shadow_blur = 0
            
        super().draw(canvas)
        
        # Dibujar borde manualmente (el base no lo hace con redondeado aún bien)
        # Por ahora usamos draw_rect para simplificar o draw_rounded_rect si está disponible
        canvas.draw_rect(abs_x, abs_y + self.height - current_border_width, self.width, current_border_width, current_border_color)

        # Dibujar Texto o Placeholder
        display_text = self.text if self.text else self.placeholder
        display_color = self.text_color if self.text else self.placeholder_color
        
        canvas.draw_text(display_text, abs_x + 8, abs_y + (self.height // 2) - 10, display_color, size=18)

        # Dibujar Cursor si está enfocado
        if self.is_focused:
            if time.time() - self.last_cursor_toggle > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_toggle = time.time()
            
            if self.cursor_visible:
                # MEDICIÓN DINÁMICA: Calculamos el ancho real del texto en píxeles
                # Usamos la misma fuente y tamaño que en draw_text
                font_name = "Roboto-Regular.ttf"
                font_path = canvas.get_asset_path(f"assets/fonts/{font_name}")
                font_key = f"{font_path}_18"
                
                cursor_offset_x = 0
                import sdl2.sdlttf
                
                if self.text and font_key in canvas._font_cache:
                    font = canvas._font_cache[font_key]
                    tw, th = sdl2.c_int(), sdl2.c_int()
                    sdl2.sdlttf.TTF_SizeUTF8(font, self.text.encode('utf-8'), tw, th)
                    cursor_offset_x = tw.value
                elif self.text:
                    # Fallback si por alguna razón la fuente no está en caché aún
                    cursor_offset_x = len(self.text) * 9

                cursor_x = abs_x + 8 + cursor_offset_x
                canvas.draw_rect(cursor_x, abs_y + 10, 2, self.height - 20, self.border_color)

    def on_blur(self):
        """Método llamado por MobileApp cuando este widget pierde el foco."""
        self.is_focused = False
        self.events.on_blur.emit()

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False

        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == "touch_down":
            if self.is_point_inside(ex, ey):
                from core.app import MobileApp
                MobileApp.INSTANCE.set_focus(self)
                return True
            else:
                # Si el clic es fuera y yo soy el que tiene el foco, lo soltamos
                from core.app import MobileApp
                if MobileApp.INSTANCE.focused_widget == self:
                    MobileApp.INSTANCE.set_focus(None)
                return False

        if self.is_focused:
            if etype == "text_input":
                self.text += event.get('text', '')
                self.events.on_change.emit()
                return True
            elif etype == "key_down":
                key = event.get('key')
                if key == sdl2.SDLK_BACKSPACE:
                    if len(self.text) > 0:
                        self.text = self.text[:-1]
                        self.events.on_change.emit()
                elif key == sdl2.SDLK_RETURN:
                    self.is_focused = False
                    sdl2.SDL_StopTextInput()
                return True
        
        return False
