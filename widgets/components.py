# widgets/components.py
# Componentes Icónicos de Android para PyPhonOS
# FAB, Snackbar mejorado, y soporte de iconos con Material Symbols (texto-glyph).

import time
import sdl2
from .base import Widget
from .button import Button
from .label import Label
from .layouts import HorizontalLayout, VerticalLayout
from renderer.colors import Palette, Color


# ─────────────────────────────────────────────
# HELPER: ICONO DE MATERIAL SYMBOLS
# ─────────────────────────────────────────────

class Icon(Widget):
    """
    Dibuja un icono usando Material Symbols (fuente de iconos).
    Si la fuente no está disponible, muestra un fallback de texto.

    Uso:
        icon = Icon("search", size=24, color=Palette.PRIMARY)
        icon = Icon("settings", size=28)
    """
    # Tabla de ligaduras de Material Symbols (texto ➜ glifo)
    ICON_MAP = {
        # Navegación
        "home":           "⌂",
        "search":         "⌕",
        "settings":       "⚙",
        "menu":           "≡",
        "back":           "←",
        "forward":        "→",
        "up":             "↑",
        "close":          "✕",
        "check":          "✓",
        "add":            "+",
        # Acciones
        "edit":           "✎",
        "delete":         "🗑",
        "share":          "↗",
        "download":       "↓",
        "upload":         "↑",
        "refresh":        "↺",
        "favorite":       "♡",
        "favorite_fill":  "♥",
        "star":           "☆",
        "star_fill":      "★",
        "bookmark":       "☆",
        "notification":   "🔔",
        "info":           "ℹ",
        "warning":        "⚠",
        "error":          "✗",
        # Media
        "play":           "▶",
        "pause":          "⏸",
        "stop":           "⏹",
        "skip_next":      "⏭",
        "skip_prev":      "⏮",
        "volume":         "🔊",
        "mute":           "🔇",
        "camera":         "📷",
        "photo":          "🖼",
        # Comunicación
        "chat":           "💬",
        "email":          "✉",
        "phone":          "📞",
        "call":           "☎",
        # Personas
        "person":         "👤",
        "group":          "👥",
        "account":        "○",
        # Estado
        "wifi":           "📶",
        "bluetooth":      "B",
        "battery":        "🔋",
        "lock":           "🔒",
        "unlock":         "🔓",
        "visibility":     "👁",
        "visibility_off": "🚫",
    }

    def __init__(self, icon_name: str, size: int = 24, color: Color = None, **kwargs):
        super().__init__(width=size, height=size, background_color=Color(0, 0, 0, 0), **kwargs)
        self.icon_name = icon_name
        self.size = size
        self.color = color or Palette.PRIMARY
        self.font_name = "MaterialSymbols-Regular.ttf"  # Requiere la fuente instalada
        self._fallback_char = self.ICON_MAP.get(icon_name, icon_name[0].upper())

    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()

        # Intentar dibujar con fuente de iconos, si no usar fallback
        try:
            canvas.draw_text(
                self._fallback_char,
                abs_x, abs_y + (self.size - 20) // 2,
                self.color,
                size=self.size - 4,
                font_name=self.font_name
            )
        except Exception:
            # Fallback: texto simple o símbolo unicode
            canvas.draw_text(
                self._fallback_char,
                abs_x, abs_y + (self.size - 20) // 2,
                self.color,
                size=max(12, self.size - 4)
            )

    def handle_event(self, event):
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)
        if etype == 'touch_up' and self.is_point_inside(ex, ey):
            self.events.on_click.emit()
            return True
        return False


# ─────────────────────────────────────────────
# FAB - FLOATING ACTION BUTTON
# ─────────────────────────────────────────────

class FAB(Widget):
    """
    Floating Action Button - Botón circular flotante.
    Aparece sobre el contenido principal y representa la acción primaria.

    Uso:
        fab = FAB(icon="add", x=300, y=700, on_click=mi_accion)
        app.add_widget(fab)
    """
    def __init__(self, icon="add", label=None, size=56, x=0, y=0,
                 color=None, icon_color=None, on_click=None,
                 extended=False, **kwargs):
        w = (len(label or "") * 10 + size + 16) if extended else size
        super().__init__(x=x, y=y, width=w, height=size, **kwargs)
        self.icon_name = icon
        self.label_text = label
        self.size = size
        self.extended = extended
        self.background_color = color or Palette.PRIMARY
        self.icon_color = icon_color or Palette.ON_PRIMARY
        self.border_radius = size // 2  # Completamente circular
        self._pressed = False
        self._hover = False

        if on_click:
            self.events.on_click.connect(on_click)

    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()

        # Color con efecto hover/press
        color = self.background_color
        if self._pressed:
            color = self.background_color.darken(0.2)
        elif self._hover:
            color = self.background_color.brighten(0.1)

        # Sombra propia del FAB (elevación 6dp)
        canvas.draw_circle(
            abs_x + self.width // 2,
            abs_y + self.height // 2 + 4,
            self.width // 2,
            0x000000,
            alpha=40
        )
        canvas.draw_circle(
            abs_x + self.width // 2,
            abs_y + self.height // 2 + 2,
            self.width // 2,
            0x000000,
            alpha=25
        )

        # Fondo circular
        canvas.draw_circle(
            abs_x + self.width // 2,
            abs_y + self.height // 2,
            self.width // 2,
            color,
            alpha=color.a
        )

        # Icono centrado
        icon_char = Icon.ICON_MAP.get(self.icon_name, "+")
        icon_size = self.size // 2
        text_x = abs_x + self.width // 2 - icon_size // 2
        text_y = abs_y + self.height // 2 - icon_size // 2
        canvas.draw_text(icon_char, text_x, text_y, self.icon_color, size=icon_size)

        # Etiqueta en FAB extendido
        if self.extended and self.label_text:
            label_x = text_x + icon_size + 8
            canvas.draw_text(self.label_text, label_x, text_y, self.icon_color, size=16)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == 'touch_down' and self.is_point_inside(ex, ey):
            self._pressed = True
            # Efecto de pulso al pulsar
            from core.animation import AnimationManager
            if AnimationManager.INSTANCE:
                AnimationManager.INSTANCE.pulse(self, scale_factor=0.92)
            return True
        elif etype == 'touch_up':
            if self._pressed and self.is_point_inside(ex, ey):
                self.events.on_click.emit()
            self._pressed = False
            return True

        return False


# ─────────────────────────────────────────────
# SNACKBAR - NOTIFICACIÓN TEMPORAL
# ─────────────────────────────────────────────

class Snackbar(Widget):
    """
    Snackbar de Material Design 3.
    Aparece desde abajo, muestra un mensaje y desaparece automáticamente.

    Uso:
        snack = Snackbar("Archivo guardado", action_text="DESHACER", on_action=mi_fn)
        app.add_widget(snack)
        snack.show()
    """
    def __init__(self, message="", action_text=None, on_action=None,
                 duration=3.5, width=320, **kwargs):
        super().__init__(
            x=0, y=0,  # Posición calculada en draw()
            width=width, height=52,
            background_color=Color(32, 32, 32, 245),
            **kwargs
        )
        self.message = message
        self.action_text = action_text
        self.on_action = on_action
        self.duration = duration
        self.border_radius = 8
        self.visible = False
        self._show_time = 0

    def show(self):
        """Muestra el Snackbar con animación de deslizamiento."""
        self.visible = True
        self._show_time = time.time()
        # El posicionamiento final se calcula en draw() según el padre

    def dismiss(self):
        self.visible = False

    def draw(self, canvas):
        if not self.visible:
            return

        # Auto-dismiss por tiempo
        if time.time() - self._show_time > self.duration:
            self.visible = False
            return

        # Calcular posición: centrado abajo, justo encima de la NavBar
        parent_w = self.parent.width if self.parent else 360
        parent_h = self.parent.height if self.parent else 800
        self.x = (parent_w - self.width) // 2
        self.y = parent_h - self.height - 90  # 90px desde abajo (navBar + margen)

        abs_x, abs_y = self.get_absolute_position()

        # Fondo redondeado oscuro
        canvas.draw_rounded_rect(
            abs_x, abs_y, self.width, self.height,
            self.border_radius, self.background_color, alpha=self.background_color.a
        )

        # Mensaje
        text_color = Color(255, 255, 255)
        msg_x = abs_x + 16
        msg_y = abs_y + (self.height - 18) // 2
        canvas.draw_text(self.message, msg_x, msg_y, text_color, size=15)

        # Botón de acción
        if self.action_text:
            action_color = Palette.PRIMARY.brighten(0.3)
            action_x = abs_x + self.width - len(self.action_text) * 10 - 16
            canvas.draw_text(self.action_text, action_x, msg_y, action_color, size=14)

    def handle_event(self, event):
        if not self.visible:
            return False
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == 'touch_up' and self.is_point_inside(ex, ey):
            if self.action_text and self.on_action:
                # Comprobar si el toque fue sobre el botón de acción
                abs_x, abs_y = self.get_absolute_position()
                action_start_x = abs_x + self.width - len(self.action_text) * 10 - 24
                if ex >= action_start_x:
                    self.on_action()
            self.dismiss()
            return True
        return False


# ─────────────────────────────────────────────
# ICON BUTTON
# ─────────────────────────────────────────────

class IconButton(Widget):
    """
    Botón con icono sin texto, estilo Material You.
    Incluye efecto de ripple al tocar.

    Uso:
        btn = IconButton("search", on_click=lambda: buscar())
    """
    def __init__(self, icon: str, size: int = 40, icon_size: int = 24,
                 color: Color = None, variant: str = "standard",
                 on_click=None, **kwargs):
        super().__init__(width=size, height=size, **kwargs)
        self.icon_name = icon
        self.size = size
        self.icon_size = icon_size
        self.color = color or Palette.PRIMARY
        self.variant = variant  # "standard", "filled", "outlined", "tonal"
        self.border_radius = size // 2
        self._pressed = False

        if variant == "filled":
            self.background_color = Palette.PRIMARY
        elif variant == "tonal":
            self.background_color = Palette.SURFACE_V
        elif variant == "outlined":
            self.background_color = Color(0, 0, 0, 0)
            self.border_width = 1
        else:  # standard
            self.background_color = Color(0, 0, 0, 0)

        if on_click:
            self.events.on_click.connect(on_click)

    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()
        cx = abs_x + self.size // 2
        cy = abs_y + self.size // 2
        r = self.size // 2

        # Fondo según variante
        if self.variant in ("filled", "tonal"):
            canvas.draw_circle(cx, cy, r, self.background_color, alpha=self.background_color.a)
        elif self.variant == "outlined":
            canvas.draw_circle(cx, cy, r, Palette.OUTLINE, alpha=60)

        # Ripple al presionar
        if self._pressed:
            canvas.draw_circle(cx, cy, r, self.color, alpha=30)

        # Icono
        icon_char = Icon.ICON_MAP.get(self.icon_name, self.icon_name[:1])
        icon_x = abs_x + (self.size - self.icon_size) // 2
        icon_y = abs_y + (self.size - self.icon_size) // 2
        icon_color = Palette.ON_PRIMARY if self.variant == "filled" else self.color
        canvas.draw_text(icon_char, icon_x, icon_y, icon_color, size=self.icon_size)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)
        if etype == 'touch_down' and self.is_point_inside(ex, ey):
            self._pressed = True
            return True
        elif etype == 'touch_up':
            was_pressed = self._pressed
            self._pressed = False
            if was_pressed and self.is_point_inside(ex, ey):
                self.events.on_click.emit()
                return True
        return False


# ─────────────────────────────────────────────
# CHIP - Etiqueta interactiva
# ─────────────────────────────────────────────

class Chip(Widget):
    """
    Chip de Material Design 3. Compacto y seleccionable.
    Tipos: 'assist', 'filter', 'input', 'suggestion'

    Uso:
        chip = Chip("Python", selected=True)
        chip.on_select = lambda s: print(f"Seleccionado: {s}")
    """
    def __init__(self, label: str, selected: bool = False,
                 chip_type: str = "filter", icon: str = None,
                 on_select=None, **kwargs):
        h = kwargs.pop('height', 34)
        w = kwargs.pop('width', max(72, len(label) * 9 + 28))
        super().__init__(width=w, height=h, **kwargs)
        self.label = label
        self.selected = selected
        self.chip_type = chip_type
        self.icon_name = icon
        self.on_select = on_select
        self.border_radius = h // 2
        self._update_colors()

    def _update_colors(self):
        if self.selected:
            self.background_color = Palette.PRIMARY_CONTAINER if hasattr(Palette, 'PRIMARY_CONTAINER') else Palette.SURFACE_V
            self.border_width = 0
        else:
            self.background_color = Color(0, 0, 0, 0)
            self.border_width = 1

    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()

        # Fondo del chip
        if self.selected:
            canvas.draw_rounded_rect(abs_x, abs_y, self.width, self.height,
                                     self.border_radius, Palette.SURFACE_V, alpha=255)
        else:
            canvas.draw_rounded_rect(abs_x, abs_y, self.width, self.height,
                                     self.border_radius, Palette.OUTLINE, alpha=50)

        # Icono de check si está seleccionado (filter chip)
        text_offset_x = 12
        if self.selected and self.chip_type == "filter":
            canvas.draw_text("✓", abs_x + 10, abs_y + 8, Palette.PRIMARY, size=14)
            text_offset_x = 26

        # Texto del label
        text_color = Palette.PRIMARY if self.selected else Palette.GRAY_700
        canvas.draw_text(self.label, abs_x + text_offset_x,
                         abs_y + (self.height - 16) // 2, text_color, size=14)

    def handle_event(self, event):
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)
        if etype == 'touch_up' and self.is_point_inside(ex, ey):
            self.selected = not self.selected
            self._update_colors()
            if callable(self.on_select):
                self.on_select(self.selected)
            self.events.on_click.emit()
            return True
        return False
