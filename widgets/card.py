# widgets/card.py
from .layouts import VerticalLayout
from renderer.colors import Palette

class Card(VerticalLayout):
    def __init__(self, elevation=4, corner_radius=12, padding=16, spacing=8, **kwargs):
        """
        Tarjeta con elevación, sombras y bordes redondeados.
        Organiza automáticamente a sus hijos de forma vertical.
        
        Args:
            elevation (int): Nivel de elevación que afecta la sombra.
            corner_radius (int): Radio de los bordes.
            padding (int): Margen interno.
            spacing (int): Espacio entre los elementos de la tarjeta.
            **kwargs: Parámetros adicionales de VerticalLayout.
        """
        super().__init__(padding=padding, spacing=spacing, **kwargs)
        self.background_color = kwargs.get('background_color', Palette.SURFACE)
        self.border_radius = corner_radius
        
        # Diseño Plano "Modern Flat": Sin sombras, borde sutil de 1px
        self.border_width = 1
        self.shadow_blur = 0
        self.shadow_offset = (0, 0)

