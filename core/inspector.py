# core/inspector.py
# Widget Inspector — Herramienta de Debug en Tiempo Real para PyPhonOS
# Activar con F12. Dibuja bordes, IDs y propiedades sobre cada widget.

from renderer.colors import Color, Palette


class WidgetInspector:
    """
    Modo debug visual para PyPhonOS.
    Cuando está activo, dibuja bordes de colores alrededor de cada widget
    y muestra sus propiedades (ID, tamaño, clase) al hacer hover/click.

    Uso:
        inspector = WidgetInspector()
        # En el loop de MobileApp:
        if tecla == F12: inspector.toggle()
        inspector.draw(canvas, widgets)
    """

    def __init__(self):
        self.enabled = False
        self.selected_widget = None
        self._hover_widget = None
        self._mouse_x = 0
        self._mouse_y = 0

        # Colores del inspector
        self._border_color = Color(0, 150, 255, 180)     # Azul para bordes
        self._selected_color = Color(255, 100, 0, 200)   # Naranja para seleccionado
        self._padding_color = Color(0, 200, 100, 60)     # Verde para padding
        self._margin_color = Color(255, 200, 0, 60)      # Amarillo para margin
        self._info_bg = Color(20, 20, 30, 230)           # Fondo del tooltip
        self._info_text = Color(220, 220, 255)            # Texto del tooltip

    def toggle(self):
        """Activa/desactiva el inspector."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.selected_widget = None
            self._hover_widget = None
        print(f"[Inspector] {'Activado ✓' if self.enabled else 'Desactivado'}")

    def handle_event(self, event, widgets):
        """Intercepta eventos para seleccionar widgets en modo debug."""
        if not self.enabled:
            return False

        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == 'touch_move' or etype == 'touch_down':
            self._mouse_x = ex
            self._mouse_y = ey

        if etype == 'touch_down':
            # Encontrar el widget más profundo bajo el cursor
            found = self._find_deepest_widget(widgets, ex, ey)
            self.selected_widget = found
            if found:
                self._print_widget_info(found)
            return True  # Consumir evento en modo debug

        return False

    def _find_deepest_widget(self, widgets, x, y):
        """Busca recursivamente el widget más profundo bajo las coordenadas."""
        result = None
        for widget in widgets:
            if not getattr(widget, 'visible', True):
                continue
            if widget.is_point_inside(x, y):
                result = widget
                # Buscar en hijos (más profundo)
                deeper = self._find_deepest_widget(
                    getattr(widget, 'children', []), x, y
                )
                if deeper:
                    result = deeper
        return result

    def draw(self, canvas, widgets):
        """Dibuja overlays del inspector sobre todos los widgets visibles."""
        if not self.enabled:
            return

        # 1. Dibujar bordes de todos los widgets recursivamente
        self._draw_widget_borders(canvas, widgets, depth=0)

        # 2. Dibujar información del widget seleccionado
        if self.selected_widget:
            self._draw_widget_info(canvas, self.selected_widget)

        # 3. Indicador "INSPECTOR ON"
        canvas.draw_rect(0, 0, 120, 20, self._info_bg, alpha=200)
        canvas.draw_text("🔍 INSPECTOR", 4, 2, self._info_text, size=11)

    def _draw_widget_borders(self, canvas, widgets, depth=0):
        """Dibuja bordes de debug alrededor de cada widget."""
        # Colores rotativos por profundidad
        depth_colors = [
            Color(0, 150, 255, 100),    # Azul
            Color(255, 100, 200, 100),  # Rosa
            Color(100, 255, 100, 100),  # Verde
            Color(255, 200, 50, 100),   # Amarillo
            Color(200, 100, 255, 100),  # Púrpura
        ]
        color = depth_colors[depth % len(depth_colors)]

        for widget in widgets:
            if not getattr(widget, 'visible', True):
                continue

            abs_x, abs_y = widget.get_absolute_position()
            w, h = widget.width, widget.height

            is_selected = widget is self.selected_widget

            # Borde del widget
            border_c = self._selected_color if is_selected else color
            thickness = 2 if is_selected else 1

            # Dibujar los 4 lados del borde
            canvas.draw_rect(abs_x, abs_y, w, thickness, border_c, alpha=border_c.a)
            canvas.draw_rect(abs_x, abs_y + h - thickness, w, thickness, border_c, alpha=border_c.a)
            canvas.draw_rect(abs_x, abs_y, thickness, h, border_c, alpha=border_c.a)
            canvas.draw_rect(abs_x + w - thickness, abs_y, thickness, h, border_c, alpha=border_c.a)

            # Dibujar padding si existe
            padding = getattr(widget, 'padding', 0)
            if padding > 0 and is_selected:
                canvas.draw_rect(abs_x, abs_y, w, padding, self._padding_color, alpha=40)
                canvas.draw_rect(abs_x, abs_y + h - padding, w, padding, self._padding_color, alpha=40)
                canvas.draw_rect(abs_x, abs_y, padding, h, self._padding_color, alpha=40)
                canvas.draw_rect(abs_x + w - padding, abs_y, padding, h, self._padding_color, alpha=40)

            # Etiqueta de clase (solo en profundidad baja o si está seleccionado)
            if depth < 2 or is_selected:
                class_name = type(widget).__name__
                label = f"{class_name}"
                if getattr(widget, 'id', None):
                    label = f"#{widget.id} {label}"
                canvas.draw_rect(abs_x, abs_y - 13, len(label) * 6 + 4, 13, border_c, alpha=180)
                canvas.draw_text(label, abs_x + 2, abs_y - 12, Color(255, 255, 255), size=10)

            # Recursión en hijos
            children = getattr(widget, 'children', [])
            if children:
                self._draw_widget_borders(canvas, children, depth + 1)

    def _draw_widget_info(self, canvas, widget):
        """Dibuja un panel de información detallada del widget seleccionado."""
        abs_x, abs_y = widget.get_absolute_position()
        info_lines = [
            f"Clase: {type(widget).__name__}",
            f"ID: {getattr(widget, 'id', 'N/A')}",
            f"Posición: ({abs_x}, {abs_y})",
            f"Tamaño: {widget.width} × {widget.height}",
            f"Visible: {getattr(widget, 'visible', True)}",
            f"Enabled: {getattr(widget, 'enabled', True)}",
            f"Hijos: {len(getattr(widget, 'children', []))}",
        ]

        # Propiedades extra
        if hasattr(widget, 'text'):
            info_lines.append(f"Text: \"{getattr(widget, 'text', '')}\"")
        if hasattr(widget, 'padding'):
            info_lines.append(f"Padding: {widget.padding}")
        if hasattr(widget, 'spacing'):
            info_lines.append(f"Spacing: {widget.spacing}")
        if hasattr(widget, 'border_radius'):
            info_lines.append(f"Radius: {widget.border_radius}")
        if hasattr(widget, 'background_color') and widget.background_color:
            bg = widget.background_color
            info_lines.append(f"BG: rgba({bg.r},{bg.g},{bg.b},{bg.a})")
        if hasattr(widget, 'is_focused'):
            info_lines.append(f"Focused: {widget.is_focused}")

        # Calcular posición del panel (evitar desbordamiento)
        panel_w = 200
        panel_h = len(info_lines) * 16 + 12
        panel_x = min(self._mouse_x + 12, 360 - panel_w - 8)
        panel_y = min(self._mouse_y + 12, 800 - panel_h - 8)
        panel_x = max(4, panel_x)
        panel_y = max(4, panel_y)

        # Fondo del panel
        canvas.draw_rect(panel_x - 1, panel_y - 1, panel_w + 2, panel_h + 2,
                         Color(0, 150, 255), alpha=180)
        canvas.draw_rect(panel_x, panel_y, panel_w, panel_h,
                         self._info_bg, alpha=240)

        # Líneas de texto
        for i, line in enumerate(info_lines):
            text_color = Color(100, 200, 255) if i == 0 else self._info_text
            canvas.draw_text(line, panel_x + 8, panel_y + 6 + i * 16, text_color, size=11)

    def _print_widget_info(self, widget):
        """Imprime info del widget seleccionado en la consola (útil para debug)."""
        abs_x, abs_y = widget.get_absolute_position()
        print(f"[Inspector] Seleccionado: {type(widget).__name__}"
              f" | ID={getattr(widget, 'id', 'N/A')}"
              f" | pos=({abs_x},{abs_y})"
              f" | size={widget.width}x{widget.height}"
              f" | hijos={len(getattr(widget, 'children', []))}")
