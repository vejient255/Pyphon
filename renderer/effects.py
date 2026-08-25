# renderer/effects.py
# Efectos Visuales Premium para PyPhonOS
# Glassmorphism, Sombras Dinámicas y Motor de Contraste WCAG.

import math
from renderer.colors import Color, Palette


class ContrastEngine:
    """
    Motor de contraste adaptativo.
    Calcula automáticamente si un texto debe ser blanco o negro
    según el color de fondo, cumpliendo con WCAG AA (ratio ≥ 4.5:1).

    Uso:
        text_color = ContrastEngine.get_text_color(background_color)
        label.color = text_color
    """

    @staticmethod
    def relative_luminance(color):
        """Calcula la luminancia relativa según WCAG 2.0."""
        def linearize(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * linearize(color.r) + 0.7152 * linearize(color.g) + 0.0722 * linearize(color.b)

    @staticmethod
    def contrast_ratio(color1, color2):
        """Calcula el ratio de contraste entre dos colores (1:1 a 21:1)."""
        l1 = ContrastEngine.relative_luminance(color1)
        l2 = ContrastEngine.relative_luminance(color2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def get_text_color(background, light=None, dark=None):
        """
        Retorna automáticamente blanco o negro según el fondo.
        
        Args:
            background: Color de fondo
            light: Color claro personalizado (default: blanco)
            dark: Color oscuro personalizado (default: negro)
        """
        light = light or Color(255, 255, 255)
        dark = dark or Color(29, 27, 32)

        ratio_light = ContrastEngine.contrast_ratio(background, light)
        ratio_dark = ContrastEngine.contrast_ratio(background, dark)

        return light if ratio_light > ratio_dark else dark

    @staticmethod
    def meets_wcag_aa(foreground, background, large_text=False):
        """Verifica si el par de colores cumple WCAG AA."""
        ratio = ContrastEngine.contrast_ratio(foreground, background)
        threshold = 3.0 if large_text else 4.5
        return ratio >= threshold

    @staticmethod
    def suggest_accessible_color(background, base_color, target="aa"):
        """Sugiere un ajuste del base_color para cumplir contraste mínimo."""
        threshold = 4.5 if target == "aa" else 7.0
        color = Color(base_color.r, base_color.g, base_color.b, base_color.a)
        
        # Intentar oscureciendo
        for i in range(50):
            if ContrastEngine.contrast_ratio(color, background) >= threshold:
                return color
            color = color.darken(0.02)
        
        # Si no se logra, intentar aclarando
        color = Color(base_color.r, base_color.g, base_color.b, base_color.a)
        for i in range(50):
            if ContrastEngine.contrast_ratio(color, background) >= threshold:
                return color
            color = color.brighten(0.02)
        
        return base_color


class DynamicShadow:
    """
    Sombra que varía según la posición Y del widget en la pantalla.
    Los widgets más arriba tienen sombra más sutil; más abajo, más pronunciada.
    Simula una fuente de luz cenital.

    Uso:
        shadow = DynamicShadow(screen_height=800)
        blur, offset_y, alpha = shadow.calculate(widget_y=300, widget_height=100)
    """

    def __init__(self, screen_height=800, light_y=0, max_blur=16, max_alpha=50):
        self.screen_height = screen_height
        self.light_y = light_y       # Posición Y de la "fuente de luz"
        self.max_blur = max_blur
        self.max_alpha = max_alpha

    def calculate(self, widget_y, widget_height=0, elevation=4):
        """
        Calcula parámetros de sombra dinámicos.

        Returns:
            (blur, offset_y, alpha) → parámetros para draw_shadow()
        """
        # Normalizar posición: 0.0 (arriba) → 1.0 (abajo)
        center_y = widget_y + widget_height / 2
        normalized = max(0.0, min(1.0, center_y / self.screen_height))

        # La sombra crece con la distancia a la fuente de luz
        factor = 0.4 + normalized * 0.6  # Rango: 0.4 → 1.0

        blur = int(self.max_blur * factor * (elevation / 8.0))
        offset_y = int(2 + 4 * factor * (elevation / 8.0))
        alpha = int(self.max_alpha * factor * (elevation / 8.0))

        return max(1, blur), max(1, offset_y), max(5, min(80, alpha))

    def draw(self, canvas, x, y, w, h, elevation=4):
        """Dibuja una sombra dinámica directamente en el canvas."""
        blur, offset_y, alpha = self.calculate(y, h, elevation)
        canvas.draw_shadow(x, y + offset_y, w, h, radius=blur, intensity=alpha)


class GlassPanel:
    """
    Panel con efecto Glassmorphism (cristal esmerilado).
    Simula blur de fondo usando capas semi-transparentes.

    Nota: El blur real de framebuffer es costoso en SDL2 puro.
    Esta implementación usa un efecto visual aproximado con:
    1. Overlay semi-transparente tintado
    2. Borde sutil brillante (frost edge)
    3. Ruido sutil para dar textura de cristal

    Uso:
        glass = GlassPanel()
        glass.draw(canvas, x=10, y=100, w=340, h=200, radius=16)
    """

    def __init__(self, tint_color=None, blur_intensity=0.6, frost_alpha=40):
        self.tint_color = tint_color or Color(255, 255, 255, 30)
        self.blur_intensity = blur_intensity  # 0.0-1.0
        self.frost_alpha = frost_alpha
        self.border_alpha = 80

    def draw(self, canvas, x, y, w, h, radius=16):
        """Dibuja el panel de cristal esmerilado."""
        
        # 1. Capa base semi-transparente (simula el blur)
        base_alpha = int(180 * self.blur_intensity)
        canvas.draw_rounded_rect(
            x, y, w, h, radius,
            Color(240, 240, 245, base_alpha),
            alpha=base_alpha
        )

        # 2. Segunda capa con tinte (color del cristal)
        canvas.draw_rounded_rect(
            x, y, w, h, radius,
            self.tint_color,
            alpha=self.tint_color.a
        )

        # 3. Gradiente de "frost" en la parte superior (brillo sutil)
        frost_h = min(h // 3, 60)
        for i in range(frost_h):
            alpha = int(self.frost_alpha * (1.0 - i / frost_h))
            if alpha > 0:
                canvas.draw_rect(x + radius, y + i, w - 2 * radius, 1,
                                 0xFFFFFF, alpha=alpha)

        # 4. Borde luminoso sutil (efecto de cristal)
        border_color = Color(255, 255, 255, self.border_alpha)
        # Borde superior
        canvas.draw_rect(x + radius, y, w - 2 * radius, 1, border_color, alpha=self.border_alpha)
        # Borde izquierdo
        canvas.draw_rect(x, y + radius, 1, h - 2 * radius, border_color, alpha=self.border_alpha // 2)
        # Borde derecho
        canvas.draw_rect(x + w - 1, y + radius, 1, h - 2 * radius, border_color, alpha=self.border_alpha // 2)

    def draw_dark(self, canvas, x, y, w, h, radius=16):
        """Variante oscura del glass (para modo nocturno)."""
        base_alpha = int(160 * self.blur_intensity)
        canvas.draw_rounded_rect(
            x, y, w, h, radius,
            Color(20, 20, 30, base_alpha),
            alpha=base_alpha
        )

        # Tinte oscuro
        canvas.draw_rounded_rect(
            x, y, w, h, radius,
            Color(40, 40, 60, 40),
            alpha=40
        )

        # Frost superior tenue
        frost_h = min(h // 4, 40)
        for i in range(frost_h):
            alpha = int(self.frost_alpha // 2 * (1.0 - i / frost_h))
            if alpha > 0:
                canvas.draw_rect(x + radius, y + i, w - 2 * radius, 1,
                                 0xFFFFFF, alpha=alpha)

        # Borde luminoso sutil
        canvas.draw_rect(x + radius, y, w - 2 * radius, 1, 0xFFFFFF, alpha=30)
