# core/navigator.py
# Sistema de Navegación por Pilas (Navigation Stack) para PyPhonOS
# Incluye transiciones animadas y gestos de borde (Edge Gestures).

import time


class Screen:
    """
    Representa una pantalla completa de la aplicación.
    Cada Screen tiene su propia jerarquía de widgets.

    Uso:
        class HomeScreen(Screen):
            def build(self):
                self.add(Label(text="Home"))
                self.add(Button(text="Ir a Ajustes", on_click=lambda: nav.push(SettingsScreen())))
    """
    def __init__(self, name="Screen", **kwargs):
        self.name = name
        self.widgets = []
        self.x_offset = 0      # Para animaciones de transición
        self.opacity = 1.0     # Para fade transitions
        self.visible = True
        self._built = False

    def build(self):
        """Override en subclases para construir la UI de la pantalla."""
        pass

    def add(self, widget):
        """Añade un widget a esta pantalla."""
        self.widgets.append(widget)

    def on_enter(self):
        """Llamado cuando la pantalla se hace visible (entra al frente)."""
        pass

    def on_leave(self):
        """Llamado cuando la pantalla sale del frente (va al fondo o se destruye)."""
        pass

    def on_resume(self):
        """Llamado cuando la pantalla vuelve al frente (back desde otra)."""
        pass

    def draw(self, canvas):
        """Dibuja todos los widgets de la pantalla con offset de transición."""
        if not self.visible:
            return
        for widget in self.widgets:
            # Aplicar offset horizontal para animaciones de slide
            original_x = widget.x
            widget.x = widget.x + int(self.x_offset)
            if hasattr(widget, 'visible') and widget.visible:
                widget.draw(canvas)
            widget.x = original_x

    def handle_event(self, event):
        """Propaga eventos a los widgets de la pantalla."""
        if not self.visible:
            return False
        # Ajustar coordenadas del evento por el offset de transición
        adjusted = dict(event)
        if 'x' in adjusted:
            adjusted['x'] = adjusted['x'] - int(self.x_offset)
        for widget in reversed(self.widgets):
            if widget.handle_event(adjusted):
                return True
        return False

    def find_by_id(self, widget_id):
        """Busca un widget por ID en toda la jerarquía de la pantalla."""
        for widget in self.widgets:
            found = widget.find_by_id(widget_id)
            if found:
                return found
        return None


class Transition:
    """Motor de transiciones entre pantallas."""

    SLIDE_LEFT  = "slide_left"   # Nueva pantalla entra desde la derecha
    SLIDE_RIGHT = "slide_right"  # Pantalla sale hacia la derecha (back)
    FADE        = "fade"
    NONE        = "none"

    def __init__(self, kind="slide_left", duration=0.28):
        self.kind = kind
        self.duration = duration
        self._start_time = None
        self._finished = False
        self.entering = None  # Screen que entra
        self.leaving = None   # Screen que sale

    @property
    def finished(self):
        return self._finished

    def start(self, entering, leaving, screen_width=360):
        self.entering = entering
        self.leaving = leaving
        self._screen_width = screen_width
        self._start_time = time.time()
        self._finished = False

        # Posiciones iniciales
        if self.kind == self.SLIDE_LEFT:
            if entering:
                entering.x_offset = screen_width
                entering.visible = True
        elif self.kind == self.SLIDE_RIGHT:
            if entering:
                entering.x_offset = -screen_width * 0.3
                entering.visible = True
        elif self.kind == self.FADE:
            if entering:
                entering.opacity = 0.0
                entering.visible = True

    def update(self):
        """Avanza la transición. Retorna True si sigue activa."""
        if self._finished or self._start_time is None:
            return False

        elapsed = time.time() - self._start_time
        t = min(elapsed / self.duration, 1.0)

        # Curva ease_out
        eased = t * (2.0 - t)

        if self.kind == self.SLIDE_LEFT:
            # Entering: derecha → centro
            if self.entering:
                self.entering.x_offset = self._screen_width * (1.0 - eased)
            # Leaving: centro → ligeramente izquierda (parallax)
            if self.leaving:
                self.leaving.x_offset = -self._screen_width * 0.3 * eased

        elif self.kind == self.SLIDE_RIGHT:
            # Entering: ligeramente izquierda → centro
            if self.entering:
                self.entering.x_offset = -self._screen_width * 0.3 * (1.0 - eased)
            # Leaving: centro → derecha
            if self.leaving:
                self.leaving.x_offset = self._screen_width * eased

        elif self.kind == self.FADE:
            if self.entering:
                self.entering.opacity = eased
            if self.leaving:
                self.leaving.opacity = 1.0 - eased

        if t >= 1.0:
            self._finish()
            return False
        return True

    def _finish(self):
        """Finaliza la transición, normaliza las posiciones."""
        if self.entering:
            self.entering.x_offset = 0
            self.entering.opacity = 1.0
            self.entering.visible = True
        if self.leaving:
            self.leaving.x_offset = 0
            self.leaving.opacity = 1.0
            if self.kind != self.FADE:
                self.leaving.visible = False
            else:
                self.leaving.visible = False
        self._finished = True


class Navigator:
    """
    Gestor de navegación entre pantallas con pila (stack).

    Uso:
        nav = Navigator(app, screen_width=360)
        nav.push(HomeScreen())          # Navega a Home
        nav.push(SettingsScreen())      # Empuja Settings encima
        nav.pop()                       # Vuelve a Home con animación slide-right

    Integración con MobileApp:
        - Se instancia automáticamente en app.__init__
        - app.navigator.push(screen) para navegar
    """

    def __init__(self, screen_width=360):
        self._stack = []            # Pila de Screen
        self._transition = None     # Transición activa
        self._screen_width = screen_width

        # Edge Gesture state
        self._edge_touch_start = None
        self._edge_dragging = False
        self._edge_drag_x = 0
        self._edge_threshold = 25   # Pixeles desde borde izquierdo para detectar
        self._edge_min_distance = 80  # Distancia mínima para completar back

    @property
    def current_screen(self):
        return self._stack[-1] if self._stack else None

    @property
    def can_go_back(self):
        return len(self._stack) > 1

    @property
    def stack_depth(self):
        return len(self._stack)

    def push(self, screen, transition="slide_left"):
        """Navega a una nueva pantalla (la añade al tope de la pila)."""
        if not screen._built:
            screen.build()
            screen._built = True

        leaving = self.current_screen
        self._stack.append(screen)

        # Iniciar transición
        if leaving and transition != "none":
            self._transition = Transition(transition, duration=0.28)
            self._transition.start(screen, leaving, self._screen_width)
        else:
            screen.visible = True
            screen.x_offset = 0

        screen.on_enter()

    def pop(self, transition="slide_right"):
        """Vuelve a la pantalla anterior (saca del tope de la pila)."""
        if not self.can_go_back:
            return None

        leaving = self._stack.pop()
        entering = self.current_screen

        if entering:
            entering.visible = True
            entering.on_resume()

        if transition != "none":
            self._transition = Transition(transition, duration=0.25)
            self._transition.start(entering, leaving, self._screen_width)
        else:
            leaving.visible = False

        leaving.on_leave()
        return leaving

    def replace(self, screen, transition="fade"):
        """Reemplaza la pantalla actual sin apilar (ej: login → home)."""
        if not screen._built:
            screen.build()
            screen._built = True

        leaving = self._stack.pop() if self._stack else None
        self._stack.append(screen)

        if leaving and transition != "none":
            self._transition = Transition(transition, duration=0.3)
            self._transition.start(screen, leaving, self._screen_width)
        else:
            screen.visible = True
            screen.x_offset = 0

        screen.on_enter()
        if leaving:
            leaving.on_leave()

    def pop_to_root(self):
        """Regresa directamente a la primera pantalla de la pila."""
        while len(self._stack) > 1:
            leaving = self._stack.pop()
            leaving.visible = False
            leaving.on_leave()
        if self._stack:
            root = self._stack[0]
            root.visible = True
            root.x_offset = 0
            root.on_resume()

    def update(self):
        """Llamar en cada frame para avanzar las transiciones."""
        if self._transition and not self._transition.finished:
            self._transition.update()

    def handle_event(self, event):
        """
        Maneja eventos de navegación:
        - Edge gesture (deslizar desde borde izquierdo)
        - Propaga eventos a la pantalla actual
        """
        etype = event.get('type')
        ex = event.get('x', 0)
        ey = event.get('y', 0)

        # --- EDGE GESTURE: deslizar desde el borde izquierdo para volver ---
        if self.can_go_back:
            if etype == 'touch_down' and ex <= self._edge_threshold:
                self._edge_touch_start = (ex, ey)
                self._edge_dragging = False
                self._edge_drag_x = 0
                return True

            elif etype == 'touch_move' and self._edge_touch_start:
                dx = ex - self._edge_touch_start[0]
                if dx > 10:
                    self._edge_dragging = True
                    self._edge_drag_x = dx
                    # Mover la pantalla actual en tiempo real
                    if self.current_screen:
                        # La pantalla debajo se asoma
                        if len(self._stack) >= 2:
                            prev_screen = self._stack[-2]
                            prev_screen.visible = True
                            prev_screen.x_offset = -self._screen_width * 0.3 * (1.0 - dx / self._screen_width)
                        self.current_screen.x_offset = dx
                return True

            elif etype == 'touch_up' and self._edge_touch_start:
                if self._edge_dragging:
                    if self._edge_drag_x >= self._edge_min_distance:
                        # Completar el back
                        self.pop()
                    else:
                        # Cancelar: regresar la pantalla a su posición
                        if self.current_screen:
                            self.current_screen.x_offset = 0
                        if len(self._stack) >= 2:
                            self._stack[-2].visible = False
                self._edge_touch_start = None
                self._edge_dragging = False
                self._edge_drag_x = 0
                return True

        # --- Propagar evento a la pantalla actual ---
        if self.current_screen:
            return self.current_screen.handle_event(event)

        return False

    def draw(self, canvas):
        """Dibuja la pila de pantallas visible."""
        # Si hay transición activa, dibujar ambas pantallas
        if self._transition and not self._transition.finished:
            if self._transition.leaving:
                self._transition.leaving.draw(canvas)
            if self._transition.entering:
                self._transition.entering.draw(canvas)
        elif self._edge_dragging and len(self._stack) >= 2:
            # Durante el edge gesture, dibujar ambas
            self._stack[-2].draw(canvas)
            self.current_screen.draw(canvas)
        elif self.current_screen:
            self.current_screen.draw(canvas)
