# widgets/responsive.py
# Layouts Adaptativos (Responsive) para PyPhonOS
# Cambia automáticamente entre 1-N columnas según el ancho de la ventana.

from .base import Widget
from .layouts import VerticalLayout, HorizontalLayout
from renderer.colors import Palette, Color


# ─────────────────────────────────────────
# BREAKPOINTS (Material Design 3)
# ─────────────────────────────────────────

class Breakpoint:
    """Puntos de quiebre estándar de Material Design 3."""
    COMPACT    = 0     # < 600px  (Móvil vertical)
    MEDIUM     = 600   # 600-839  (Móvil horizontal / Tablet vertical)
    EXPANDED   = 840   # 840-1199 (Tablet horizontal)
    LARGE      = 1200  # >= 1200  (Desktop)

    @staticmethod
    def get_class(width):
        """Retorna la clase de tamaño basado en el ancho."""
        if width < 600:
            return "compact"
        elif width < 840:
            return "medium"
        elif width < 1200:
            return "expanded"
        return "large"


class ResponsiveLayout(Widget):
    """
    Layout que reorganiza sus hijos automáticamente según el ancho disponible.

    En modo COMPACT (< 600px): 1 columna vertical
    En modo MEDIUM (600-839px): 2 columnas
    En modo EXPANDED (840-1199px): 3 columnas
    En modo LARGE (>= 1200px): 4 columnas

    Uso:
        responsive = ResponsiveLayout(width=360, height=600, spacing=16, padding=16)
        responsive.add_item(Card(width=160, height=120))
        responsive.add_item(Card(width=160, height=120))
        responsive.add_item(Card(width=160, height=120))
        # En 360px → se apilan verticalmente
        # En 840px → se muestran en 3 columnas
    """

    def __init__(self, spacing=12, padding=16, custom_breakpoints=None, **kwargs):
        super().__init__(**kwargs)
        self.spacing = spacing
        self.padding = padding
        self._items = []
        self._columns = 1
        self._last_width = 0

        # Breakpoints personalizables
        self.breakpoints = custom_breakpoints or {
            "compact":  1,
            "medium":   2,
            "expanded": 3,
            "large":    4,
        }

    def add_item(self, widget):
        """Añade un widget al layout responsive."""
        widget.parent = self
        self._items.append(widget)
        self._recalculate()

    def remove_item(self, widget):
        """Elimina un widget del layout responsive."""
        self._items = [w for w in self._items if w is not widget]
        self._recalculate()

    def set_breakpoints(self, compact=1, medium=2, expanded=3, large=4):
        """Configura las columnas por breakpoint."""
        self.breakpoints = {
            "compact": compact, "medium": medium,
            "expanded": expanded, "large": large,
        }
        self._recalculate()

    def _recalculate(self):
        """Recalcula posiciones según el ancho actual."""
        size_class = Breakpoint.get_class(self.width)
        self._columns = self.breakpoints.get(size_class, 1)

        if not self._items:
            return

        available_w = self.width - self.padding * 2
        col_w = (available_w - self.spacing * (self._columns - 1)) // self._columns

        current_x = self.padding
        current_y = self.padding
        col_index = 0
        row_max_h = 0

        for item in self._items:
            item.width = col_w
            item.x = current_x
            item.y = current_y

            row_max_h = max(row_max_h, item.height)
            col_index += 1

            if col_index >= self._columns:
                # Siguiente fila
                col_index = 0
                current_x = self.padding
                current_y += row_max_h + self.spacing
                row_max_h = 0
            else:
                current_x += col_w + self.spacing

        # Actualizar altura del contenedor
        total_rows = (len(self._items) + self._columns - 1) // self._columns
        if self._items:
            avg_h = sum(i.height for i in self._items) / len(self._items)
            self.height = max(self.height, int(self.padding * 2 + total_rows * (avg_h + self.spacing)))

    def draw(self, canvas):
        """Dibuja con recálculo si el ancho cambió."""
        if self.width != self._last_width:
            self._last_width = self.width
            self._recalculate()

        # Fondo
        if self.background_color and self.background_color.a > 0:
            abs_x, abs_y = self.get_absolute_position()
            canvas.draw_rect(abs_x, abs_y, self.width, self.height,
                             self.background_color, alpha=self.background_color.a)

        # Dibujar items
        for item in self._items:
            item.draw(canvas)

    def handle_event(self, event):
        for item in reversed(self._items):
            if item.handle_event(event):
                return True
        return super().handle_event(event)


class AdaptiveScaffold(Widget):
    """
    Scaffold que se adapta entre móvil y tablet/desktop.

    En COMPACT: Drawer oculto como overlay, contenido ocupa todo el ancho.
    En EXPANDED: Drawer siempre visible a la izquierda, contenido a la derecha.

    Uso:
        scaffold = AdaptiveScaffold(width=360, height=800)
        scaffold.drawer_content = mi_menu_lateral
        scaffold.main_content = mi_contenido_principal
    """

    def __init__(self, drawer_width=280, **kwargs):
        super().__init__(**kwargs)
        self.drawer_width = drawer_width
        self._drawer_content = None
        self._main_content = None
        self._drawer_open = False  # Solo relevante en modo compact

    @property
    def drawer_content(self):
        return self._drawer_content

    @drawer_content.setter
    def drawer_content(self, widget):
        self._drawer_content = widget
        if widget:
            widget.parent = self

    @property
    def main_content(self):
        return self._main_content

    @main_content.setter
    def main_content(self, widget):
        self._main_content = widget
        if widget:
            widget.parent = self

    @property
    def is_expanded(self):
        return self.width >= Breakpoint.MEDIUM

    def toggle_drawer(self):
        """Abre/cierra el drawer en modo compact."""
        self._drawer_open = not self._drawer_open

    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()

        if self.is_expanded:
            # Modo EXPANDED: drawer siempre visible a la izquierda
            if self._drawer_content:
                self._drawer_content.x = 0
                self._drawer_content.y = 0
                self._drawer_content.width = self.drawer_width
                self._drawer_content.height = self.height
                self._drawer_content.draw(canvas)

            if self._main_content:
                self._main_content.x = self.drawer_width
                self._main_content.y = 0
                self._main_content.width = self.width - self.drawer_width
                self._main_content.height = self.height
                self._main_content.draw(canvas)
        else:
            # Modo COMPACT: contenido ocupa todo
            if self._main_content:
                self._main_content.x = 0
                self._main_content.y = 0
                self._main_content.width = self.width
                self._main_content.height = self.height
                self._main_content.draw(canvas)

            # Drawer como overlay si está abierto
            if self._drawer_open and self._drawer_content:
                # Scrim (fondo oscuro semi-transparente)
                canvas.draw_rect(abs_x, abs_y, self.width, self.height,
                                 0x000000, alpha=100)
                self._drawer_content.x = 0
                self._drawer_content.y = 0
                self._drawer_content.width = self.drawer_width
                self._drawer_content.height = self.height
                self._drawer_content.draw(canvas)

    def handle_event(self, event):
        etype = event.get('type')
        ex = event.get('x', 0)

        if not self.is_expanded and self._drawer_open:
            # En modo compact con drawer abierto, tap fuera cierra
            if etype == 'touch_down' and ex > self.drawer_width:
                self._drawer_open = False
                return True
            if self._drawer_content and ex <= self.drawer_width:
                return self._drawer_content.handle_event(event)

        if self.is_expanded and self._drawer_content:
            if ex <= self.drawer_width:
                return self._drawer_content.handle_event(event)

        if self._main_content:
            return self._main_content.handle_event(event)

        return False


class MediaQuery:
    """
    Utilidad para consultar el tamaño de pantalla actual.

    Uso:
        mq = MediaQuery(app_width=360)
        if mq.is_compact:
            # Layout de una columna
        elif mq.is_expanded:
            # Layout de tres columnas
    """

    def __init__(self, app_width=360, app_height=800):
        self.width = app_width
        self.height = app_height

    @property
    def size_class(self):
        return Breakpoint.get_class(self.width)

    @property
    def is_compact(self):
        return self.width < 600

    @property
    def is_medium(self):
        return 600 <= self.width < 840

    @property
    def is_expanded(self):
        return 840 <= self.width < 1200

    @property
    def is_large(self):
        return self.width >= 1200

    @property
    def is_portrait(self):
        return self.height > self.width

    @property
    def is_landscape(self):
        return self.width >= self.height

    @property
    def aspect_ratio(self):
        return self.width / max(1, self.height)
