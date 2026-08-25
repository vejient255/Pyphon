from .base import Widget
from renderer.colors import Palette, Color
from renderer.lighting import LightingEngine, NEUMORPHIC_DEFAULT

class NeumorphicWidget(Widget):
    """
    Widget especializado con efecto neumórfico automático.
    Hereda todas las propiedades de Widget pero activa neumorfismo por defecto.
    """
    def __init__(self, **kwargs):
        # Activar neumorfismo por defecto
        kwargs['neumorphic'] = kwargs.get('neumorphic', True)
        # Configurar elevación y bordes redondeados por defecto
        kwargs['elevation'] = kwargs.get('elevation', 1.2)
        kwargs['border_radius'] = kwargs.get('border_radius', 16)
        # Usar color base neumórfico si no se especifica
        if 'background_color' not in kwargs:
            kwargs['background_color'] = Color(
                NEUMORPHIC_DEFAULT['surface'] >> 16 & 0xFF,
                NEUMORPHIC_DEFAULT['surface'] >> 8 & 0xFF,
                NEUMORPHIC_DEFAULT['surface'] & 0xFF,
                255
            )
        super().__init__(**kwargs)
    
    def set_pressed(self, pressed):
        """Cambia el estado presionado manualmente"""
        self.is_pressed = pressed


class GlassmorphismPanel(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.Color(255, 255, 255, 50)
        
    def draw(self, canvas):
        canvas.draw_rect(self.x, self.y, self.width, self.height, self.background_color, filled=True)


class DynamicIsland(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.BLACK
        self.border_radius = 20
        self.width = 120
        self.height = 35
        self.expanded = False
        
    def expand(self):
        self.width = 300
        self.height = 100
        self.expanded = True


class NeumorphicButton(NeumorphicWidget):
    """Botón con efecto neumórfico y respuesta táctil visual"""
    def __init__(self, text="", icon=None, on_click=None, **kwargs):
        super().__init__(on_click=on_click, **kwargs)
        self.text = text
        self.icon = icon
        if 'width' not in kwargs or 'height' not in kwargs:
            padding = 40
            self.width = max(kwargs.get('width', 120), len(text) * 20 + padding)
            self.height = max(kwargs.get('height', 50), 50)
    
    def draw(self, canvas):
        super().draw(canvas)
        abs_x, abs_y = self.get_absolute_position()
        if self.text:
            text_width = len(self.text) * 14
            text_x = abs_x + (self.width - text_width) // 2
            text_y = abs_y + (self.height - 20) // 2
            text_color = Color(100, 100, 100, 255) if self.is_pressed else Color(51, 51, 51, 255)
            canvas.draw_text(self.text, text_x, text_y, 
                           (text_color.r << 16) | (text_color.g << 8) | text_color.b)


class NeumorphicContainer(NeumorphicWidget):
    """Contenedor neumórfico para agrupar elementos"""
    def __init__(self, **kwargs):
        kwargs['elevation'] = kwargs.get('elevation', 0.8)
        super().__init__(**kwargs)
