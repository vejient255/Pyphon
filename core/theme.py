# core/theme.py
# Motor de Temas Dinámicos para PyPhonOS - Material You
# Soporte para Modo Oscuro/Claro y paletas de acento dinámicas.

from renderer.colors import Color, Palette


# ─────────────────────────────────────────────
# 1. DEFINICIÓN DE TEMAS
# ─────────────────────────────────────────────

class Theme:
    """Representa un conjunto completo de tokens de color para un tema."""

    def __init__(self, name, data: dict):
        self.name = name
        for key, value in data.items():
            setattr(self, key, value)


# Tema Claro (Material Design 3 - Light)
LIGHT_THEME = Theme("light", {
    "primary":           Color(103, 80, 164),    # Deep Purple
    "on_primary":        Color(255, 255, 255),
    "primary_container": Color(234, 221, 255),
    "secondary":         Color(98, 91, 113),
    "on_secondary":      Color(255, 255, 255),
    "error":             Color(179, 38, 30),
    "on_error":          Color(255, 255, 255),
    "background":        Color(254, 247, 255),   # Soft Lavender White
    "on_background":     Color(29, 27, 32),
    "surface":           Color(255, 255, 255),
    "surface_variant":   Color(231, 224, 236),
    "on_surface":        Color(29, 27, 32),
    "on_surface_variant":Color(74, 68, 88),
    "outline":           Color(121, 116, 126),
    "outline_variant":   Color(202, 196, 208),
    "inverse_surface":   Color(50, 47, 53),
    "inverse_on_surface":Color(245, 239, 247),
    "scrim":             Color(0, 0, 0, 130),
    "shadow":            Color(0, 0, 0, 30),
    "text_primary":      Color(29, 27, 32),
    "text_secondary":    Color(74, 68, 88),
    "text_hint":         Color(121, 116, 126),
    "divider":           Color(202, 196, 208),
    "card":              Color(255, 255, 255),
    "status_bar":        Color(254, 247, 255),
})

# Tema Oscuro (Material Design 3 - Dark)
DARK_THEME = Theme("dark", {
    "primary":           Color(208, 188, 255),   # Light Purple
    "on_primary":        Color(55, 30, 115),
    "primary_container": Color(79, 55, 139),
    "secondary":         Color(204, 194, 220),
    "on_secondary":      Color(51, 45, 65),
    "error":             Color(242, 184, 181),
    "on_error":          Color(96, 20, 16),
    "background":        Color(20, 18, 24),      # Deep dark navy
    "on_background":     Color(231, 224, 236),
    "surface":           Color(29, 27, 32),
    "surface_variant":   Color(74, 68, 88),
    "on_surface":        Color(231, 224, 236),
    "on_surface_variant":Color(202, 196, 208),
    "outline":           Color(150, 142, 165),
    "outline_variant":   Color(74, 68, 88),
    "inverse_surface":   Color(231, 224, 236),
    "inverse_on_surface":Color(50, 47, 53),
    "scrim":             Color(0, 0, 0, 160),
    "shadow":            Color(0, 0, 0, 80),
    "text_primary":      Color(231, 224, 236),
    "text_secondary":    Color(202, 196, 208),
    "text_hint":         Color(150, 142, 165),
    "divider":           Color(74, 68, 88),
    "card":              Color(40, 38, 44),
    "status_bar":        Color(20, 18, 24),
})


# ─────────────────────────────────────────────
# 2. PALETAS DE ACENTO (Material You Seeds)
# ─────────────────────────────────────────────

ACCENT_PURPLE = {"primary": Color(103, 80, 164), "primary_container": Color(234, 221, 255)}
ACCENT_BLUE   = {"primary": Color(0, 99, 154),   "primary_container": Color(207, 229, 255)}
ACCENT_GREEN  = {"primary": Color(32, 107, 48),  "primary_container": Color(165, 251, 183)}
ACCENT_PINK   = {"primary": Color(160, 42, 87),  "primary_container": Color(255, 216, 228)}
ACCENT_ORANGE = {"primary": Color(162, 78, 0),   "primary_container": Color(255, 220, 191)}
ACCENT_TEAL   = {"primary": Color(0, 105, 117),  "primary_container": Color(151, 240, 253)}

ACCENTS = {
    "purple": ACCENT_PURPLE,
    "blue":   ACCENT_BLUE,
    "green":  ACCENT_GREEN,
    "pink":   ACCENT_PINK,
    "orange": ACCENT_ORANGE,
    "teal":   ACCENT_TEAL,
}


# ─────────────────────────────────────────────
# 3. THEME MANAGER: CONTROLADOR GLOBAL
# ─────────────────────────────────────────────

class ThemeManager:
    """
    Gestor central de temas de PyPhonOS.
    Controla el tema activo (Claro/Oscuro) y el color de acento.

    Uso:
        from core.theme import ThemeManager
        theme = ThemeManager()   # Se instancia en MobileApp

        # Cambiar a modo oscuro
        theme.set_dark_mode(True)

        # Cambiar color de acento
        theme.set_accent("blue")

        # Obtener un color para usar en un widget
        color = theme.primary
        widget.background_color = color

        # Escuchar cambios de tema
        theme.on_change = lambda: mi_app.reiniciar_colores()
    """

    INSTANCE = None

    def __init__(self, dark_mode=False, accent="purple"):
        self._dark_mode = dark_mode
        self._accent = accent
        self._base_theme = DARK_THEME if dark_mode else LIGHT_THEME
        self._listeners = []  # Callbacks a llamar al cambiar de tema
        self.on_change = None  # Callback único opcional

        ThemeManager.INSTANCE = self
        self._apply_to_palette()

    @property
    def is_dark(self) -> bool:
        return self._dark_mode

    @property
    def current_theme(self) -> Theme:
        return self._base_theme

    def _get_accent_colors(self) -> dict:
        return ACCENTS.get(self._accent, ACCENT_PURPLE)

    def _apply_to_palette(self):
        """Sincroniza los colores del tema activo con la clase Palette global."""
        t = self._base_theme
        accent = self._get_accent_colors()

        Palette.PRIMARY    = accent.get("primary", t.primary)
        Palette.BACKGROUND = t.background
        Palette.SURFACE    = t.surface
        Palette.SURFACE_V  = t.surface_variant
        Palette.OUTLINE    = t.outline
        Palette.ON_PRIMARY = t.on_primary
        Palette.SECONDARY  = t.secondary
        Palette.GRAY_900   = t.text_primary
        Palette.GRAY_700   = t.text_secondary
        Palette.GRAY_500   = t.text_hint
        Palette.GRAY_300   = t.divider

    def set_dark_mode(self, enabled: bool):
        """Activa o desactiva el Modo Oscuro. Notifica a todos los listeners."""
        if self._dark_mode == enabled:
            return
        self._dark_mode = enabled
        self._base_theme = DARK_THEME if enabled else LIGHT_THEME
        self._apply_to_palette()
        self._notify()

    def toggle_dark_mode(self):
        """Alterna entre Modo Oscuro y Modo Claro."""
        self.set_dark_mode(not self._dark_mode)

    def set_accent(self, accent_name: str):
        """
        Cambia el color de acento de la UI.
        Opciones disponibles: 'purple', 'blue', 'green', 'pink', 'orange', 'teal'
        """
        if accent_name not in ACCENTS:
            raise ValueError(f"Acento '{accent_name}' no encontrado. Opciones: {list(ACCENTS.keys())}")
        self._accent = accent_name
        self._apply_to_palette()
        self._notify()

    def set_custom_accent(self, primary_color: Color, container_color: Color = None):
        """Define un color de acento personalizado (RGB libre)."""
        ACCENTS["custom"] = {
            "primary": primary_color,
            "primary_container": container_color or primary_color.brighten(0.4)
        }
        self._accent = "custom"
        self._apply_to_palette()
        self._notify()

    def add_listener(self, callback):
        """Registra un callback para ser notificado al cambiar de tema."""
        self._listeners.append(callback)

    def remove_listener(self, callback):
        self._listeners = [l for l in self._listeners if l is not callback]

    def _notify(self):
        """Notifica a todos los listeners registrados."""
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                print(f"[ThemeManager] Error en listener: {e}")
        if callable(self.on_change):
            self.on_change()

    # Accesos rápidos (proxies directos al tema activo + acento)
    @property
    def primary(self) -> Color:
        return ACCENTS.get(self._accent, ACCENT_PURPLE)["primary"]

    @property
    def primary_container(self) -> Color:
        return ACCENTS.get(self._accent, ACCENT_PURPLE).get("primary_container", self._base_theme.primary_container)

    @property
    def background(self) -> Color:
        return self._base_theme.background

    @property
    def surface(self) -> Color:
        return self._base_theme.surface

    @property
    def on_surface(self) -> Color:
        return self._base_theme.on_surface

    @property
    def on_background(self) -> Color:
        return self._base_theme.on_background

    @property
    def card(self) -> Color:
        return self._base_theme.card

    @property
    def text_primary(self) -> Color:
        return self._base_theme.text_primary

    @property
    def text_secondary(self) -> Color:
        return self._base_theme.text_secondary

    @property
    def outline(self) -> Color:
        return self._base_theme.outline

    @property
    def scrim(self) -> Color:
        return self._base_theme.scrim

    @property
    def shadow(self) -> Color:
        return self._base_theme.shadow

    # ─── Hot-Reload de Temas ───

    def enable_hot_reload(self, json_path, check_interval=1.0):
        """
        Activa la recarga automática de temas desde un archivo JSON.
        El archivo se monitorea en cada frame y si cambia, se aplican los nuevos colores.

        Formato del JSON:
        {
            "dark_mode": false,
            "accent": "blue",
            "overrides": {
                "background": [254, 247, 255],
                "primary": [0, 99, 154]
            }
        }

        Args:
            json_path: Ruta al archivo theme.json
            check_interval: Segundos entre verificaciones (default: 1s)
        """
        import os
        self._hot_reload_path = json_path
        self._hot_reload_interval = check_interval
        self._hot_reload_last_check = 0
        self._hot_reload_last_mtime = 0
        self._hot_reload_enabled = True

        if os.path.exists(json_path):
            self._hot_reload_last_mtime = os.path.getmtime(json_path)
            self._load_theme_json(json_path)
        print(f"[ThemeManager] Hot-Reload activado: {json_path}")

    def check_hot_reload(self):
        """Verificar si el archivo de tema cambió (llamar en cada frame o periódicamente)."""
        import os, time as _time
        if not getattr(self, '_hot_reload_enabled', False):
            return

        now = _time.time()
        if now - self._hot_reload_last_check < self._hot_reload_interval:
            return
        self._hot_reload_last_check = now

        try:
            mtime = os.path.getmtime(self._hot_reload_path)
            if mtime != self._hot_reload_last_mtime:
                self._hot_reload_last_mtime = mtime
                self._load_theme_json(self._hot_reload_path)
                print(f"[ThemeManager] Tema recargado desde {self._hot_reload_path}")
        except (OSError, FileNotFoundError):
            pass

    def _load_theme_json(self, path):
        """Carga y aplica un archivo de tema JSON."""
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Aplicar modo oscuro
            if "dark_mode" in data:
                self._dark_mode = data["dark_mode"]
                self._base_theme = DARK_THEME if self._dark_mode else LIGHT_THEME

            # Aplicar acento
            if "accent" in data:
                accent_name = data["accent"]
                if accent_name in ACCENTS:
                    self._accent = accent_name

            # Aplicar overrides de colores personalizados
            overrides = data.get("overrides", {})
            for key, value in overrides.items():
                if isinstance(value, list) and len(value) >= 3:
                    a = value[3] if len(value) > 3 else 255
                    color = Color(value[0], value[1], value[2], a)
                    setattr(self._base_theme, key, color)

            self._apply_to_palette()
            self._notify()

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"[ThemeManager] Error cargando tema JSON: {e}")

    def save_theme_json(self, path):
        """Exporta el tema actual a un archivo JSON."""
        import json
        data = {
            "dark_mode": self._dark_mode,
            "accent": self._accent,
            "overrides": {}
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"[ThemeManager] Tema guardado en {path}")
