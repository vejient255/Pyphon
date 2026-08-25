# widgets/label.py
from .base import Widget
from renderer.colors import Palette
import sdl2.sdlttf
import sdl2
import os

class Label(Widget):
    def __init__(self, text="HOLA", x=0, y=0, width=None, height=None, size=20, color=None, align="left"):
        """
        Widget de texto con soporte para alineación y caracteres Unicode (UTF-8).
        """
        # Estimación de tamaño si no se proporciona para evitar colapsos en layouts
        w = width if width else (len(text) * (size // 2))
        h = height if height else size + 10
        
        # Inicializamos con background_color=None para que las etiquetas sean transparentes
        super().__init__(x, y, w, h, background_color=None)
        
        self.text = text
        self.size = size 
        self.text_color = color if color else Palette.GRAY_900
        self.align = align

    def draw(self, canvas):
        """
        Renderiza el texto calculando el desplazamiento necesario para la alineación.
        """
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        # Elegir fuente según tamaño (Heurística simple para modernizar)
        nombre_fuente = "Roboto-Bold.ttf" if self.size > 24 else "Roboto-Regular.ttf"
        if self.size <= 14:
            nombre_fuente = "Roboto-Light.ttf"
        
        # 1. Obtener la ruta y clave de la fuente
        font_path = canvas.get_asset_path(os.path.join("assets", "fonts", nombre_fuente))
        font_key = f"{font_path}_{self.size}"
        
        # Por defecto, el renderizado empieza en el X absoluto (alineación izquierda)
        render_x = abs_x
        
        # 2. Lógica de alineación usando medidas reales de la fuente
        # Aseguramos que la fuente esté en caché para poder medirla
        if font_key not in canvas._font_cache:
             if os.path.exists(font_path):
                canvas._font_cache[font_key] = sdl2.sdlttf.TTF_OpenFont(font_path.encode('utf-8'), self.size)

        if font_key in canvas._font_cache:
            font = canvas._font_cache[font_key]
            w, h = sdl2.c_int(), sdl2.c_int()
            
            # --- CORRECCIÓN PARA CARACTERES ESPECIALES ---
            # Usamos TTF_SizeUTF8 para medir correctamente el ancho de textos con tildes o eñes
            sdl2.sdlttf.TTF_SizeUTF8(font, str(self.text).encode('utf-8'), w, h)
            
            if self.align == "center":
                render_x = abs_x + (self.width // 2) - (w.value // 2)
            elif self.align == "right":
                render_x = abs_x + self.width - w.value
        
        # 3. Dibujar en el canvas con el suavizado activado
        canvas.draw_text(
            str(self.text), 
            int(render_x), 
            int(abs_y), 
            self.text_color, 
            size=self.size, 
            font_name=nombre_fuente
        )

    def get_render_data(self):
        """Mantiene compatibilidad con sistemas de renderizado externo."""
        abs_x, abs_y = self.get_absolute_position()
        return self.text, abs_x, abs_y, self.text_color, self.size