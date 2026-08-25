# widgets/image.py
from .base import Widget
from renderer.colors import Palette

class Image(Widget):
    """
    Componente de imagen avanzado para PyPhonOS.
    Soporta carga asíncrona de archivos locales (PNG, JPG, WEBP)
    y escalado tipo web (cover, contain, fill).
    """
    
    SCALE_FILL    = "fill"     # Estira la imagen para llenar el espacio
    SCALE_CONTAIN = "contain"  # Mantiene proporción, se ve completa
    SCALE_COVER   = "cover"    # Mantiene proporción, recorta para llenar
    
    def __init__(self, src, scale_mode=SCALE_COVER, **kwargs):
        super().__init__(**kwargs)
        self.src = src
        self.scale_mode = scale_mode
        self.background_color = Palette.TRANSPARENT # Base transparente
        # Hereda self.opacity y self.border_radius de Widget base
        
    def draw(self, canvas):
        if not self.visible or self.opacity <= 0:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # 1. Aplicar la lógica de base (sombra, si tiene)
        if self.shadow_blur > 0:
            canvas.draw_shadow(
                abs_x + self.shadow_offset[0], 
                abs_y + self.shadow_offset[1], 
                self.width, self.height, 
                radius=self.shadow_blur, 
                intensity=self.shadow_color.a
            )

        # 2. Dibujar la Imagen
        alpha_int = int(255 * self.opacity)
        if alpha_int > 0:
            canvas.draw_image_advanced(
                self.src, 
                abs_x, abs_y, 
                self.width, self.height, 
                scale_mode=self.scale_mode, 
                alpha=alpha_int,
                border_radius=self.border_radius
            )

        # 3. Dibujar Borde (opcional)
        if self.border_width > 0:
            canvas.draw_rounded_rect(
                abs_x, abs_y, self.width, self.height, 
                self.border_radius, self.border_color, alpha=60
            )

        # 4. Hijos encima (si se usa la imagen de fondo contenedor)
        for child in self.children:
            child.draw(canvas)
