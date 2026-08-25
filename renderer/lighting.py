# renderer/lighting.py
"""
Motor de Iluminación para Efectos Neumórficos
Calcula sombras suaves usando principios físicos de luz
"""
import math
from renderer.colors import Color, Palette

class LightingEngine:
    """Motor estático para cálculos de iluminación neumórfica"""
    
    # Ángulo de luz por defecto (superior izquierda, 45 grados)
    LIGHT_ANGLE = 315  # grados
    LIGHT_INTENSITY = 0.7
    
    @staticmethod
    def calculate_shadows(base_color, elevation=1.0, light_angle=None, light_intensity=None):
        """
        Calcula las dos sombras necesarias para el efecto neumórfico:
        - Sombra clara (highlight): lado opuesto a la fuente de luz
        - Sombra oscura (shadow): lado hacia la fuente de luz
        
        Args:
            base_color: Color base del widget (hex o Color)
            elevation: Altura simulada del elemento (0.5 a 3.0)
            light_angle: Ángulo de la fuente de luz en grados (default: 315°)
            light_intensity: Intensidad de la luz (0.3 a 1.0)
            
        Returns:
            tuple: (light_shadow_color, dark_shadow_color, offset_x, offset_y)
        """
        angle = light_angle if light_angle else LightingEngine.LIGHT_ANGLE
        intensity = light_intensity if light_intensity else LightingEngine.LIGHT_INTENSITY
        
        # Convertir color base a RGB
        if isinstance(base_color, int):
            r, g, b = LightingEngine._hex_to_rgb(base_color)
        else:
            r, g, b = base_color.r, base_color.g, base_color.b
        
        # Calcular offset basado en elevación
        offset_magnitude = elevation * 2.0
        offset_x = -math.cos(math.radians(angle)) * offset_magnitude
        offset_y = -math.sin(math.radians(angle)) * offset_magnitude
        
        # Calcular sombra clara (más brillante que la base)
        light_factor = 1.0 + (0.15 * intensity * elevation)
        light_r = min(255, int(r * light_factor))
        light_g = min(255, int(g * light_factor))
        light_b = min(255, int(b * light_factor))
        light_shadow = Color(light_r, light_g, light_b, 255)
        
        # Calcular sombra oscura (más oscura que la base)
        dark_factor = 1.0 - (0.20 * intensity * elevation)
        dark_r = max(0, int(r * dark_factor))
        dark_g = max(0, int(g * dark_factor))
        dark_b = max(0, int(b * dark_factor))
        dark_shadow = Color(dark_r, dark_g, dark_b, 255)
        
        return (light_shadow, dark_shadow, int(offset_x), int(offset_y))
    
    @staticmethod
    def calculate_pressed_shadows(base_color, depth=0.5):
        """
        Calcula sombras para estado "presionado" (efecto hundido)
        Invierte las sombras para simular que el elemento se hunde
        
        Args:
            base_color: Color base del widget
            depth: Profundidad del hundimiento (0.3 a 1.0)
            
        Returns:
            tuple: (inner_light, inner_dark, offset_x, offset_y)
        """
        # En estado presionado, las sombras se invierten
        light, dark, _, _ = LightingEngine.calculate_shadows(base_color, elevation=depth)
        
        # Invertimos: la sombra clara va abajo/derecha, la oscura arriba/izquierda
        return (dark, light, 2, 2)  # Offset pequeño hacia adentro
    
    @staticmethod
    def get_neumorphic_palette(base_hex=0xE0E5EC):
        """
        Genera una paleta completa para diseño neumórfico
        
        Args:
            base_hex: Color base de fondo (default: gris azulado suave)
            
        Returns:
            dict: Colores calculados para diferentes estados
        """
        r, g, b = LightingEngine._hex_to_rgb(base_hex)
        base_color = Color(r, g, b, 255)
        
        # Sombras para estado normal (elevado)
        light_shadow, dark_shadow, ox, oy = LightingEngine.calculate_shadows(
            base_color, elevation=1.0
        )
        
        # Sombras para estado presionado (hundido)
        pressed_light, pressed_dark, px, py = LightingEngine.calculate_pressed_shadows(
            base_color, depth=0.6
        )
        
        # Color de texto óptimo para este fondo
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        text_color = Color(51, 51, 51, 255) if luminance > 0.5 else Color(240, 240, 240, 255)
        
        return {
            'base': base_color,
            'light_shadow': light_shadow,
            'dark_shadow': dark_shadow,
            'shadow_offset': (ox, oy),
            'pressed_light': pressed_light,
            'pressed_dark': pressed_dark,
            'pressed_offset': (px, py),
            'text': text_color,
            'accent': Color(52, 152, 219, 255),  # Azul moderno
            'surface': base_hex
        }
    
    @staticmethod
    def _hex_to_rgb(color_hex):
        """Convierte entero hexadecimal a RGB"""
        c_val = int(color_hex)
        r = (c_val >> 16) & 0xFF
        g = (c_val >> 8) & 0xFF
        b = c_val & 0xFF
        return r, g, b


# Paleta neumórfica precalculada para uso rápido
NEUMORPHIC_DEFAULT = LightingEngine.get_neumorphic_palette(0xE0E5EC)
