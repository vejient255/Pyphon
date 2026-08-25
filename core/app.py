# core/app.py
import sdl2
import ctypes
from .window import NativeWindow
from renderer.canvas import Canvas
from .animation import AnimationManager
from .theme import ThemeManager
from .navigator import Navigator
from .inspector import WidgetInspector
from .i18n import I18nManager

class MobileApp:
    INSTANCE = None # Singleton para acceso global de widgets

    def __init__(self, titulo="PyPhonOS", ancho=360, alto=640):
        """
        Inicializa el motor principal de PyPhonOS.
        Ventana de tamaño fijo 360x640 (resolución base de Android) para desarrollo en PC.
        """
        MobileApp.INSTANCE = self
        
        # 0. Configuración de Calidad ANTES de crear ventana
        # Calidad de escalado: "1" = filtrado bilinear (buen equilibrio calidad/rendimiento)
        sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"1")
        
        # 1. Crear ventana con tamaño fijo de teléfono (360x640)
        self.window = NativeWindow(ancho, alto, titulo)
        self.canvas = Canvas(self.window)
        
        self.widgets = []
        self.event_overlay = None
        self.focused_widget = None
        self.running = True

        # ─── Subsistemas del Framework ───
        self.anim = AnimationManager()        # Motor de animaciones
        self.theme = ThemeManager()            # Motor de temas (light por defecto)
        self.navigator = Navigator(screen_width=ancho)  # Navegación por pilas
        self.inspector = WidgetInspector()     # Inspector de widgets (F12)
        self.i18n = I18nManager()              # Internacionalización

        # ─── Estado de pantalla ───
        self._screen_width = ancho
        self._screen_height = alto
        self._use_navigator = False  # Se activa al hacer primer push()

    def add_widget(self, widget):
        """Añade un widget a la lista de renderizado y eventos."""
        self.widgets.append(widget)

    def set_focus(self, widget):
        """Asigna el foco exclusivo a un widget y desenfoca al anterior."""
        if self.focused_widget == widget:
            return
            
        if self.focused_widget:
            if hasattr(self.focused_widget, 'on_blur'):
                self.focused_widget.on_blur()
            else:
                self.focused_widget.is_focused = False
        
        self.focused_widget = widget
        if self.focused_widget:
            self.focused_widget.is_focused = True
            sdl2.SDL_StartTextInput()
        else:
            sdl2.SDL_StopTextInput()

    # ─── Navegación ───

    def push_screen(self, screen):
        """Navega a una nueva pantalla con transición animada."""
        self._use_navigator = True
        self.navigator.push(screen)

    def pop_screen(self):
        """Vuelve a la pantalla anterior."""
        if self.navigator.can_go_back:
            self.navigator.pop()

    # ─── Eventos ───

    def _procesar_eventos(self):
        """Gestiona entrada del sistema y propagación de eventos."""
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
            
            ui_event = None
            
            # ─── MOUSE / TOUCH ───
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                ui_event = {"type": "touch_down", "x": event.button.x, "y": event.button.y, "button": event.button.button}
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                ui_event = {"type": "touch_up", "x": event.button.x, "y": event.button.y, "button": event.button.button}
            elif event.type == sdl2.SDL_MOUSEMOTION:
                if event.motion.state & sdl2.SDL_BUTTON_LMASK:
                    ui_event = {"type": "touch_move", "x": event.motion.x, "y": event.motion.y}
                else:
                    ui_event = {"type": "mouse_move", "x": event.motion.x, "y": event.motion.y}

            # ─── SCROLL WHEEL ───
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                # SDL2 reporta scroll como wheel event
                mx, my = sdl2.c_int(0), sdl2.c_int(0)
                sdl2.SDL_GetMouseState(mx, my)
                ui_event = {"type": "scroll", "x": mx.value, "y": my.value,
                            "dx": event.wheel.x, "dy": event.wheel.y}
            
            # ─── TECLADO ───
            elif event.type == sdl2.SDL_TEXTINPUT:
                ui_event = {"type": "text_input", "text": event.text.text.decode('utf-8')}
            elif event.type == sdl2.SDL_KEYDOWN:
                key = event.key.keysym.sym
                ui_event = {"type": "key_down", "key": key}

                # F12: Toggle Inspector
                if key == sdl2.SDLK_F12:
                    self.inspector.toggle()
                    continue

                # Escape / Back: Navegar hacia atrás
                if key == sdl2.SDLK_ESCAPE or key == sdl2.SDLK_AC_BACK:
                    if self._use_navigator and self.navigator.can_go_back:
                        self.navigator.pop()
                        continue

            if ui_event:
                # 0. Inspector intercepta si está activo
                if self.inspector.enabled:
                    all_widgets = self._get_all_render_targets()
                    if self.inspector.handle_event(ui_event, all_widgets):
                        continue

                # 1. Overlay tiene máxima prioridad
                if self.event_overlay:
                    if self.event_overlay.handle_event(ui_event):
                        continue
                
                # 2. Navigator (si está activo)
                if self._use_navigator:
                    if self.navigator.handle_event(ui_event):
                        continue

                # 3. Widgets normales
                for widget in reversed(self.widgets):
                    if widget.handle_event(ui_event):
                        break

    def _get_all_render_targets(self):
        """Obtiene todos los widgets visibles (para el inspector)."""
        targets = list(self.widgets)
        if self._use_navigator and self.navigator.current_screen:
            targets.extend(self.navigator.current_screen.widgets)
        return targets

    # ─── Rendering ───

    def _render_frame(self):
        """Dibuja la escena completa usando la GPU."""
        # A. Verificar Hot-Reload de temas si está activo
        self.theme.check_hot_reload()

        # B. Avanzar animaciones
        self.anim.update()

        # B. Avanzar transiciones de navegación
        if self._use_navigator:
            self.navigator.update()

        # C. Limpiar con color de fondo del tema
        bg = self.theme.background
        self.canvas.clear((bg.r << 16) | (bg.g << 8) | bg.b)
        
        # D. Dibujar widgets estáticos (debajo del navigator)
        for widget in self.widgets:
            if getattr(widget, 'visible', True):
                widget.draw(self.canvas)

        # E. Dibujar pantalla del navigator (encima)
        if self._use_navigator:
            self.navigator.draw(self.canvas)
        
        # F. Dibujar Overlays (Menús, Diálogos)
        self.canvas.draw_overlays()

        # G. Inspector (siempre encima de todo)
        if self.inspector.enabled:
            all_widgets = self._get_all_render_targets()
            self.inspector.draw(self.canvas, all_widgets)
        
        # H. Intercambio de buffers
        self.window.presentar()

    def run(self):
        """Bucle principal optimizado para 60 FPS y bajo consumo de energía."""
        print("PyPhonOS: Iniciando motor de alta resolución...")
        
        try:
            while self.running:
                self._procesar_eventos()
                self._render_frame()
                sdl2.SDL_Delay(16)  # ~60 FPS
        finally:
            self._finalizar()

    def _finalizar(self):
        """Cierre limpio de recursos."""
        print("PyPhonOS: Cerrando sesión de forma segura...")
        self.window.cerrar()

if __name__ == "__main__":
    app = MobileApp()
    app.run()