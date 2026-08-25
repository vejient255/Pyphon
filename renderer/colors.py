# PyPhonOS - colors.py
# Gestión profesional de color y transformaciones para interfaces móviles

class Color:
    """Clase base para representar colores en la interfaz."""
    
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        # Aseguramos que los valores estén en el rango 0-255
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.a = max(0, min(255, a))

    def __int__(self):
        """
        CORRECCIÓN CRÍTICA: Permite que int(objeto_color) devuelva un entero de 32 bits.
        Formato: 0xRRGGBB (Compatible con el buffer de PyPhonOS)
        """
        # Combinamos los canales usando desplazamiento de bits (Bitwise Shifting)
        return (self.r << 16) | (self.g << 8) | self.b

    def to_tuple(self):
        """Devuelve el color como tupla (R, G, B, A)."""
        return (self.r, self.g, self.b, self.a)

    def to_hex(self):
        """Convierte el color a formato hexadecimal string."""
        return "#{:02x}{:02x}{:02x}{:02x}".format(self.r, self.g, self.b, self.a)

    @staticmethod
    def from_hex(hex_str: str):
        """Crea una instancia de Color desde un string hexadecimal."""
        hex_str = hex_str.lstrip('#')
        lv = len(hex_str)
        if lv == 6: # Formato RRGGBB
            return Color(*(int(hex_str[i:i+2], 16) for i in (0, 2, 4)))
        elif lv == 8: # Formato RRGGBBAA
            return Color(*(int(hex_str[i:i+2], 16) for i in (0, 2, 4, 6)))
        raise ValueError(f"Formato hexadecimal '{hex_str}' no soportado.")

    def brighten(self, factor: float):
        """
        Aclara el color (0.0 a 1.0).
        Útil para efectos 'hover' o estados de botones.
        """
        return Color(
            int(self.r + (255 - self.r) * factor),
            int(self.g + (255 - self.g) * factor),
            int(self.b + (255 - self.b) * factor),
            self.a
        )

    def darken(self, factor: float):
        """
        Oscurece el color (0.0 a 1.0).
        Útil para simular que un botón ha sido presionado.
        """
        return Color(
            int(self.r * (1 - factor)),
            int(self.g * (1 - factor)),
            int(self.b * (1 - factor)),
            self.a
        )

# --- Paleta de Colores Predefinida (Modern Design System) ---
# Basada en Material Design 3 (M3) y principios de UI contemporánea.

class Palette:
    # Colores Base
    WHITE       = Color(255, 255, 255)
    BLACK       = Color(0, 0, 0)
    TRANSPARENT = Color(0, 0, 0, 0)
    
    # Sistema de Colores (Light Theme)
    PRIMARY    = Color(103, 80, 164)   # Deep Purple M3
    ON_PRIMARY = Color(255, 255, 255)
    SECONDARY  = Color(98, 91, 113)    # Muted Purple/Grey
    ERROR      = Color(179, 38, 30)    # Error Red
    
    # Superficies y Fondos
    BACKGROUND        = Color(254, 247, 255) # Soft Lavender White (Material 3 style)
    SURFACE           = Color(255, 255, 255) # Pure White
    SURFACE_V         = Color(238, 232, 244) # Surface Variant
    OUTLINE           = Color(121, 116, 126) 
    PRIMARY_CONTAINER     = Color(234, 221, 255) # Light purple tonal container
    ON_PRIMARY_CONTAINER  = Color(33, 0, 93)
    
    # Sombras y Efectos (con canal Alpha reducido para elegancia)
    SHADOW      = Color(0, 0, 0, 30)    # Sombra muy suave (12% opacidad)
    SHADOW_DARK = Color(0, 0, 0, 60)    # Sombra moderada
    
    # Dark Mode (Opcional)
    DARK_BG      = Color(28, 27, 31)
    DARK_SURFACE = Color(33, 31, 38)
    DARK_PRIMARY = Color(208, 188, 255)
    
    # Grises Semánticos
    GRAY_100   = Color(244, 244, 249)
    GRAY_300   = Color(224, 224, 224)
    GRAY_500   = Color(158, 158, 158)
    GRAY_700   = Color(66, 66, 66)
    GRAY_900   = Color(28, 27, 31)