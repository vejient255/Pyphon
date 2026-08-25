# widgets/utils.py
# Utilidades de interacción avanzada para PyPhonOS
# Simulación de gestos táctiles usando eventos de ratón/mouse.

import time
from .base import Widget
from renderer.colors import Palette, Color


class DragAndDrop(Widget):
    """
    Convierte cualquier widget en un elemento arrastrable.
    El widget hijo se puede mover por toda la pantalla.

    Uso:
        draggable = DragAndDrop(width=100, height=100)
        draggable.add_child(mi_card)
    """
    def __init__(self, drag_threshold=4, lock_x=False, lock_y=False, **kwargs):
        super().__init__(**kwargs)
        self.drag_threshold = drag_threshold  # Pixeles antes de activar drag
        self.lock_x = lock_x  # Si True, solo se puede mover verticalmente
        self.lock_y = lock_y  # Si True, solo se puede mover horizontalmente

        # Estado interno
        self._is_dragging = False
        self._press_start = None   # (x, y) donde se presionó
        self._drag_offset = (0, 0) # Offset entre la esquina y el punto de toque

    def handle_event(self, event):
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == 'touch_down' and self.is_point_inside(ex, ey):
            self._press_start = (ex, ey)
            # Calcular offset para que el arrastre sea natural (no saltar al centro)
            self._drag_offset = (ex - self.x, ey - self.y)
            self._is_dragging = False
            self.events.on_click.emit()
            return True

        elif etype == 'touch_move' and self._press_start:
            dist = abs(ex - self._press_start[0]) + abs(ey - self._press_start[1])
            if dist >= self.drag_threshold:
                if not self._is_dragging:
                    self._is_dragging = True
                    if hasattr(self.events, 'on_drag_start'):
                        self.events.on_drag_start.emit()

                # Actualizar posición del widget
                if not self.lock_x:
                    self.x = ex - self._drag_offset[0]
                if not self.lock_y:
                    self.y = ey - self._drag_offset[1]

                if hasattr(self.events, 'on_drag'):
                    self.events.on_drag.emit()
            return True

        elif etype == 'touch_up' and self._press_start:
            if self._is_dragging and hasattr(self.events, 'on_drag_end'):
                self.events.on_drag_end.emit()
            self._press_start = None
            self._is_dragging = False
            return True

        return super().handle_event(event)

    def draw(self, canvas):
        # Indica visualmente que está siendo arrastrado (leve transparencia)
        if self._is_dragging:
            orig_alpha = self.background_color.a if self.background_color else 255
            if self.background_color:
                self.background_color.a = max(0, orig_alpha - 50)
            super().draw(canvas)
            if self.background_color:
                self.background_color.a = orig_alpha
        else:
            super().draw(canvas)


class SwipeToAction(Widget):
    """
    Detecta gestos de deslizamiento horizontal u horizontal.
    Lanza callbacks al completar un swipe con suficiente distancia.

    Uso:
        swipe = SwipeToAction(min_distance=80)
        swipe.on_swipe_left  = lambda: print("Swipe izquierda!")
        swipe.on_swipe_right = lambda: print("Swipe derecha!")
        swipe.on_swipe_up    = lambda: print("Swipe arriba!")
        swipe.on_swipe_down  = lambda: print("Swipe abajo!")
    """
    def __init__(self, min_distance=60, max_time=0.5, **kwargs):
        super().__init__(**kwargs)
        self.min_distance = min_distance   # Pixeles mínimos para considerar swipe
        self.max_time = max_time           # Segundos máximos para completar el gesto

        # Callbacks directos (más sencillo que EventHandler para este caso)
        self.on_swipe_left  = None
        self.on_swipe_right = None
        self.on_swipe_up    = None
        self.on_swipe_down  = None

        self._touch_start = None
        self._touch_time = None

    def handle_event(self, event):
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == 'touch_down' and self.is_point_inside(ex, ey):
            self._touch_start = (ex, ey)
            self._touch_time = time.time()
            return True

        elif etype == 'touch_up' and self._touch_start:
            elapsed = time.time() - self._touch_time
            if elapsed <= self.max_time:
                dx = ex - self._touch_start[0]
                dy = ey - self._touch_start[1]
                adx, ady = abs(dx), abs(dy)

                if adx > ady and adx >= self.min_distance:
                    # Swipe horizontal
                    if dx < 0 and callable(self.on_swipe_left):
                        self.on_swipe_left()
                    elif dx > 0 and callable(self.on_swipe_right):
                        self.on_swipe_right()
                elif ady > adx and ady >= self.min_distance:
                    # Swipe vertical
                    if dy < 0 and callable(self.on_swipe_up):
                        self.on_swipe_up()
                    elif dy > 0 and callable(self.on_swipe_down):
                        self.on_swipe_down()

            self._touch_start = None
            self._touch_time = None
            return True

        return super().handle_event(event)


class PullToRefresh(Widget):
    """
    Wrapper que detecta el gesto de "tirar hacia abajo" para refrescar.
    Pensado para envolver a un ScrollView u otro layout.

    Uso:
        ptr = PullToRefresh(width=360, height=700)
        ptr.on_refresh = lambda: cargar_datos()
        ptr.add_child(mi_scroll_view)
    """
    def __init__(self, trigger_distance=60, **kwargs):
        super().__init__(**kwargs)
        self.trigger_distance = trigger_distance  # Pixeles para disparar refresh
        self.on_refresh = None  # Callback

        self._is_refreshing = False
        self._pull_start_y = None
        self._current_pull = 0  # Cuánto se ha jalado (px)
        self._refresh_color = Palette.PRIMARY

    def handle_event(self, event):
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        if etype == 'touch_down' and self.is_point_inside(ex, ey):
            self._pull_start_y = ey
            self._current_pull = 0
            return True

        elif etype == 'touch_move' and self._pull_start_y is not None:
            dy = ey - self._pull_start_y
            # Solo detectar pull hacia ABAJO (dy > 0) y solo al inicio del scroll
            if dy > 0 and not self._is_refreshing:
                # Amortiguación: resistencia al jalar
                self._current_pull = min(dy * 0.5, self.trigger_distance * 1.5)
            return True

        elif etype == 'touch_up' and self._pull_start_y is not None:
            if self._current_pull >= self.trigger_distance and not self._is_refreshing:
                self._is_refreshing = True
                if callable(self.on_refresh):
                    self.on_refresh()
            self._pull_start_y = None
            self._current_pull = 0
            self._is_refreshing = False
            return True

        return super().handle_event(event)

    def draw(self, canvas):
        abs_x, abs_y = self.get_absolute_position()

        # Dibujar el indicador de "pull to refresh" si se está jalando
        if self._current_pull > 0:
            ratio = min(self._current_pull / self.trigger_distance, 1.0)
            indicator_size = int(16 * ratio)
            indicator_x = abs_x + self.width // 2
            indicator_y = abs_y + 8 + int(self._current_pull * 0.3)
            if indicator_size > 0:
                canvas.draw_circle(
                    indicator_x, indicator_y,
                    indicator_size,
                    self._refresh_color,
                    alpha=int(200 * ratio)
                )

        super().draw(canvas)

    def stop_refresh(self):
        """Llamar externamente cuando la carga de datos haya terminado."""
        self._is_refreshing = False
        self._current_pull = 0


class InfiniteScroll(Widget):
    """
    Detecta cuándo el usuario llega al final del contenido
    y dispara el callback on_load_more para cargar más items.

    Su uso es conceptual: monitorea el offset del scroll que
    se le pase externamente. Para integrarse con ScrollView,
    llama a `check_scroll(offset, total_height, visible_height)`.
    """
    def __init__(self, threshold=50, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold  # Pixeles desde el final para disparar carga
        self.on_load_more = None    # Callback

        self._is_loading = False
        self._last_offset = 0

    def check_scroll(self, scroll_offset, total_height, visible_height):
        """
        Llamar desde el ScrollView padre en cada frame o evento de scroll.
        scroll_offset: cuántos pixeles se ha desplazado hacia abajo.
        total_height: altura total del contenido.
        visible_height: altura del área visible.
        """
        remaining = total_height - visible_height - scroll_offset
        if remaining <= self.threshold and not self._is_loading:
            self._is_loading = True
            if callable(self.on_load_more):
                self.on_load_more()
        elif remaining > self.threshold * 2:
            # Resetear cuando vuelve arriba
            self._is_loading = False

    def stop_loading(self):
        """Llamar cuando se terminen de cargar los nuevos items."""
        self._is_loading = False

    def handle_event(self, event):
        # InfiniteScroll es pasivo, no consume eventos
        return super().handle_event(event)


class ParallaxView(Widget):
    """
    Vista con capas que se desplazan a diferentes velocidades,
    creando un efecto de profundidad (parallax).

    Uso:
        pv = ParallaxView(width=360, height=500)
        pv.add_layer(fondo_widget, speed=0.2)
        pv.add_layer(medio_widget, speed=0.6)
        pv.add_layer(frente_widget, speed=1.0)
        pv.scroll_offset = 100  # Actualizar con el scroll actual
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layers = []  # Lista de (widget, speed)
        self.scroll_offset = 0  # Offset vertical del scroll principal

    def add_layer(self, widget, speed=1.0):
        """
        Añade una capa con una velocidad de parallax.
        speed=0.0 = estático, speed=1.0 = se mueve igual que el scroll.
        """
        self._layers.append({'widget': widget, 'speed': speed})
        widget.parent = self

    def draw(self, canvas):
        abs_x, abs_y = self.get_absolute_position()

        for layer in self._layers:
            widget = layer['widget']
            speed = layer['speed']

            # Calcular offset de cada capa
            parallax_offset = int(self.scroll_offset * speed)

            # Guardar posición original y aplicar offset
            original_y = widget.y
            widget.y = original_y - parallax_offset

            widget.draw(canvas)

            # Restaurar posición original
            widget.y = original_y

    def handle_event(self, event):
        for layer in self._layers:
            if layer['widget'].handle_event(event):
                return True
        return super().handle_event(event)


class ZoomableView(Widget):
    """
    Widget que soporta zoom (acercar/alejar) mediante:
    - Rueda del ratón (scroll wheel): zoom in/out.
    - Doble clic: toggle entre zoom normal y 2x.

    El widget hijo se escala visualmente.
    Emite on_zoom(scale) al cambiar el nivel de zoom.
    """
    def __init__(self, min_scale=0.5, max_scale=4.0, zoom_step=0.15, **kwargs):
        super().__init__(**kwargs)
        self.scale = 1.0
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.zoom_step = zoom_step
        self.on_zoom = None  # Callback(scale)

        self._last_click_time = 0
        self._double_click_interval = 0.3

    def zoom_in(self):
        self.scale = min(self.scale + self.zoom_step, self.max_scale)
        if callable(self.on_zoom):
            self.on_zoom(self.scale)

    def zoom_out(self):
        self.scale = max(self.scale - self.zoom_step, self.min_scale)
        if callable(self.on_zoom):
            self.on_zoom(self.scale)

    def reset_zoom(self):
        self.scale = 1.0
        if callable(self.on_zoom):
            self.on_zoom(self.scale)

    def handle_event(self, event):
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        # Rueda del ratón -> zoom
        if etype == 'scroll' and self.is_point_inside(ex, ey):
            dy = event.get('dy', 0)
            if dy > 0:
                self.zoom_in()
            elif dy < 0:
                self.zoom_out()
            return True

        # Doble clic -> toggle zoom 2x
        if etype == 'touch_down' and self.is_point_inside(ex, ey):
            now = time.time()
            if now - self._last_click_time < self._double_click_interval:
                if self.scale != 1.0:
                    self.reset_zoom()
                else:
                    self.scale = 2.0
                    if callable(self.on_zoom):
                        self.on_zoom(self.scale)
            self._last_click_time = now
            return True

        return super().handle_event(event)

    def draw(self, canvas):
        """
        Dibuja los hijos aplicando el factor de escala.
        Nota: en SDL2 puro sin OpenGL la escala se simula
        ajustando el tamaño lógico del renderer.
        """
        abs_x, abs_y = self.get_absolute_position()

        # Dibujar fondo del contenedor
        if self.background_color and self.background_color.a > 0:
            canvas.draw_rect(
                abs_x, abs_y, self.width, self.height,
                self.background_color, alpha=self.background_color.a
            )

        # Escalar posiciones y tamaños de los hijos
        cx = abs_x + self.width / 2
        cy = abs_y + self.height / 2

        for child in self.children:
            # Calcular posición escalada respecto al centro
            orig_x, orig_y = child.x, child.y
            orig_w, orig_h = child.width, child.height

            child.x = int((orig_x - self.width / 2) * self.scale + self.width / 2)
            child.y = int((orig_y - self.height / 2) * self.scale + self.height / 2)
            child.width = int(orig_w * self.scale)
            child.height = int(orig_h * self.scale)

            child.draw(canvas)

            # Restaurar
            child.x, child.y = orig_x, orig_y
            child.width, child.height = orig_w, orig_h

        # Indicador de zoom si no es 1:1
        if abs(self.scale - 1.0) > 0.05:
            zoom_text = f"{self.scale:.1f}x"
            canvas.draw_rect(abs_x + self.width - 44, abs_y + 6, 38, 18, 0x000000, alpha=90)
            canvas.draw_text(zoom_text, abs_x + self.width - 42, abs_y + 7, Palette.WHITE, size=12)


class RotateView(Widget):
    """
    Widget wrapper que simula rotación de contenido.
    En desktop, se activa con clic derecho + arrastre horizontal.
    Emite on_rotate(angle) al cambiar el ángulo.

    Nota: la rotación visual real requiere SDL_RenderCopyEx
    (solo funciona para texturas individuales). Esta implementación
    trackea el ángulo y lo expone para uso personalizado.
    """
    def __init__(self, snap_angles=None, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0.0  # Ángulo actual en grados
        self.snap_angles = snap_angles  # Lista de ángulos de "snap" ej. [0, 90, 180, 270]
        self.on_rotate = None  # Callback(angle)

        self._rotating = False
        self._rotate_start_x = None
        self._rotate_start_angle = 0.0
        self._rotation_sensitivity = 0.5  # grados por pixel

    def handle_event(self, event):
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)

        # Clic derecho (button == 3) para iniciar rotación
        if etype == 'touch_down':
            button = event.get('button', 1)
            if button == 3 and self.is_point_inside(ex, ey):
                self._rotating = True
                self._rotate_start_x = ex
                self._rotate_start_angle = self.angle
                return True

        elif etype == 'touch_move' and self._rotating:
            if self._rotate_start_x is not None:
                dx = ex - self._rotate_start_x
                self.angle = (self._rotate_start_angle + dx * self._rotation_sensitivity) % 360
                if callable(self.on_rotate):
                    self.on_rotate(self.angle)
            return True

        elif etype == 'touch_up' and self._rotating:
            # Snap al ángulo más cercano si hay snap_angles
            if self.snap_angles:
                closest = min(self.snap_angles, key=lambda a: abs(a - self.angle))
                self.angle = closest
                if callable(self.on_rotate):
                    self.on_rotate(self.angle)
            self._rotating = False
            self._rotate_start_x = None
            return True

        return super().handle_event(event)

    def draw(self, canvas):
        """
        Dibuja los hijos con rotación.
        Para textura completa con rotación real, usa draw() normal
        y aplica SDL_RenderCopyEx en texturas individuales
        (requiere un renderer de textura intermedia).
        """
        abs_x, abs_y = self.get_absolute_position()

        # Dibujar fondo
        if self.background_color and self.background_color.a > 0:
            canvas.draw_rect(
                abs_x, abs_y, self.width, self.height,
                self.background_color, alpha=self.background_color.a
            )

        # Dibujar hijos con offset de rotación simulado
        # (rotación real de escena completa no disponible en SDL2 sin texturas intermedias)
        for child in self.children:
            child.draw(canvas)

        # Indicador del ángulo si está rotando
        if self._rotating or abs(self.angle) > 0.5:
            angle_text = f"{int(self.angle)}°"
            canvas.draw_rect(abs_x + self.width - 44, abs_y + 6, 38, 18, 0x000000, alpha=90)
            canvas.draw_text(angle_text, abs_x + self.width - 42, abs_y + 7, Palette.WHITE, size=12)
