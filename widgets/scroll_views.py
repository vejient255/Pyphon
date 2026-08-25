# widgets/scroll_views.py
import sdl2
from .base import Widget
from .layouts import BoxLayout, VerticalLayout, HorizontalLayout
from renderer.colors import Palette

class ScrollView(Widget):
    def __init__(self, **kwargs):
        """Contenedor que permite desplazamiento de su contenido."""
        super().__init__(**kwargs)
        self.scroll_x = 0
        self.scroll_y = 0
        self.is_dragging = False
        self.has_moved = False
        self.last_ty = 0
        self.content_width = kwargs.get('content_width', self.width)
        self.content_height = kwargs.get('content_height', self.height)

    def add_widget(self, widget):
        """Añade un widget al contenido desplazable."""
        self.add_child(widget)

    def draw(self, canvas):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Activar clipping
        rect = sdl2.SDL_Rect(int(abs_x), int(abs_y), int(self.width), int(self.height))
        sdl2.SDL_RenderSetClipRect(canvas.renderer, rect)
        
        super().draw(canvas)
        
        # Desactivar clipping
        sdl2.SDL_RenderSetClipRect(canvas.renderer, None)

    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
            
        etype = event.get('type')
        ex, ey = event.get('x', 0), event.get('y', 0)
        
        # 1. Propagar a los hijos primero (útil para clics, sliders, etc.)
        # Si un hijo consume el evento (ej: el Slider), no debemos iniciar el scroll.
        if not self.is_dragging: 
            for child in reversed(self.children):
                if child.handle_event(event):
                    return True # Hijo consumió el evento, salimos.
                    
        # 2. Lógica interactiva del Scroll (solo si ningún hijo lo capturó)
        if etype == "touch_down" and self.is_point_inside(ex, ey):
            self.is_dragging = True
            self.has_moved = False
            self.last_ty = ey
            return True # Consumimos el down para recibir el move
            
        elif etype == "touch_move" and self.is_dragging:
            dy = ey - self.last_ty
            
            # Umbral de movimiento para considerar que es un scroll y no un tap (clic)
            if abs(dy) > 1:
                self.has_moved = True
                self.last_ty = ey
                
                # Calcular límite máximo basado en el alto del nodo hijo (la lista de contenido)
                child_h = self.children[0].height if self.children else self.height
                max_scroll = max(0, child_h - self.height)
                
                new_scroll = self.scroll_y - dy
                new_scroll = max(0, min(new_scroll, max_scroll))
                
                self.scroll_y = new_scroll
                
                if self.children:
                    # Trasladar el contenido verticalmente según el scroll
                    self.children[0].y = -self.scroll_y
                
            return True # Consume el movimiento
            
        elif etype == "touch_up":
            if self.is_dragging:
                was_scrolled = self.has_moved
                self.is_dragging = False
                
                # Si el usuario soltó sin haber movido apenas el dedo, es un clic!
                # Lo propagamos manualmente a los hijos.
                if not was_scrolled:
                    for child in reversed(self.children):
                        if child.handle_event(event):
                            return True
                return True
            
        return False

class ListView(ScrollView):
    def __init__(self, items=None, **kwargs):
        """Lista desplazable verticalmente."""
        super().__init__(**kwargs)
        self.layout = VerticalLayout(width=self.width, height=self.height)
        self.add_child(self.layout)
        if items:
            for item in items:
                self.add_item(item)

    def add_item(self, widget):
        self.layout.add_widget(widget)

class GridView(ScrollView):
    def __init__(self, columns=2, **kwargs):
        """Cuadrícula desplazable."""
        super().__init__(**kwargs)
        self.columns = columns
        # Implementación básica usando coordenadas manuales o un layout específico

class SwipeRefreshLayout(ScrollView):
    def __init__(self, on_refresh=None, **kwargs):
        """Contenedor con soporte para 'pull-to-refresh'."""
        super().__init__(**kwargs)
        self.on_refresh = on_refresh
        self.is_refreshing = False

class RecyclerView(ListView):
    def __init__(self, adapter=None, **kwargs):
        """Lista eficiente que recicla vistas (View Recycling)."""
        super().__init__(**kwargs)
        self.adapter = adapter
        self.cached_views = []

class ViewPager(Widget):
    def __init__(self, **kwargs):
        """Vista que permite deslizar horizontalmente entre páginas."""
        super().__init__(**kwargs)
        self.pages = []
        self.current_page = 0
        self.layout = HorizontalLayout(width=self.width, height=self.height)
        self.add_child(self.layout)

    def add_page(self, page_widget):
        self.pages.append(page_widget)
        self.layout.add_widget(page_widget)
