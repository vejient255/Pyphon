# widgets/navigation.py
from .base import Widget
from .layouts import HorizontalLayout, VerticalLayout, BoxLayout
from .label import Label
from .button import Button
from renderer.colors import Palette, Color

class NavigationBar(HorizontalLayout):
    """
    Barra de navegación inferior para destinos principales.
    """
    def __init__(self, x=0, y=0, width=360, height=80, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, 
                         background_color=Palette.SURFACE, 
                         spacing=0, padding=0, **kwargs)
        self.shadow_blur = 8
        self.shadow_offset = (0, -2) # Sombra hacia arriba

class Toolbar(HorizontalLayout):
    """
    Barra superior con título y acciones.
    """
    def __init__(self, title="PyPhon", x=0, y=0, width=360, height=64, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, 
                         background_color=Palette.PRIMARY, 
                         spacing=16, padding=16, **kwargs)
        self.title_label = Label(text=title, color=Palette.ON_PRIMARY, size=22)
        self.add_widget(self.title_label)
        self.shadow_blur = 4
        self.shadow_offset = (0, 2)

class TabItem(Button):
    """Ítem individual para TabLayout."""
    def __init__(self, text, active=False, **kwargs):
        super().__init__(text=text, **kwargs)
        self.active = active
        self.border_radius = 0
        self.shadow_blur = 0
        self.normal_color = Palette.TRANSPARENT
        self.active_indicator_color = Palette.PRIMARY
        self.text_color = Palette.PRIMARY if active else Palette.GRAY_700

    def draw(self, canvas):
        super().draw(canvas)
        if self.active:
            abs_x, abs_y = self.get_absolute_position()
            indicator_height = 3
            canvas.draw_rect(abs_x, abs_y + self.height - indicator_height, 
                             self.width, indicator_height, 
                             self.active_indicator_color)

class TabLayout(HorizontalLayout):
    """
    Pestañas horizontales para navegación entre vistas relacionadas.
    """
    def __init__(self, tabs=None, x=0, y=0, width=360, height=48, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, 
                         background_color=Palette.SURFACE, 
                         spacing=0, padding=0, **kwargs)
        self.tabs = tabs or []
        self._setup_tabs()

    def _setup_tabs(self):
        tab_width = self.width // max(1, len(self.tabs))
        for i, tab_text in enumerate(self.tabs):
            tab = TabItem(text=tab_text, width=tab_width, height=self.height, active=(i == 0))
            self.add_widget(tab)

class BottomNavItem(VerticalLayout):
    """Ítem para BottomNavigationView con icono (simulado) y etiqueta."""
    def __init__(self, label, active=False, **kwargs):
        super().__init__(spacing=4, padding=8, **kwargs)
        self.active = active
        self.background_color = Palette.TRANSPARENT
        
        # Centro el contenido horizontalmente
        inner_width = kwargs.get('width', 100) - 16
        
        self.icon_box = Widget(width=24, height=24, 
                               background_color=Palette.PRIMARY if active else Palette.GRAY_500)
        self.icon_box.x = (inner_width - 24) // 2
        self.icon_box.border_radius = 12
        
        self.label = Label(text=label, size=12, 
                           color=Palette.PRIMARY if active else Palette.GRAY_700,
                           align="center", width=inner_width)
        
        self.add_child(self.icon_box)
        self.add_child(self.label)

    def reposition_children(self):
        """Sobrescribimos para mantener el centrado manual del icono."""
        self.icon_box.y = self.padding
        self.label.y = self.padding + self.icon_box.height + self.spacing
        self.label.x = self.padding

class BottomNavigationView(HorizontalLayout):
    """
    Navegación inferior con iconos y etiquetas (Material Design).
    """
    def __init__(self, items=None, x=0, y=0, width=360, height=80, on_select=None, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, 
                         background_color=Palette.SURFACE, 
                         spacing=0, padding=0, **kwargs)
        self.items_labels = items or ["Home", "Search", "Settings"]
        self.widgets_items = []
        self.on_select = on_select
        self._setup_items()

    def _setup_items(self):
        item_width = self.width // max(1, len(self.items_labels))
        for i, label in enumerate(self.items_labels):
            item = BottomNavItem(label=label, width=item_width, height=self.height, active=(i == 0))
            # Capturamos el índice 'i' usando un closure correcto
            item.events.on_click.connect(lambda idx=i: self.select_item(idx))
            self.add_widget(item)
            self.widgets_items.append(item)

    def select_item(self, index):
        """Cambia el estado visual del ítem seleccionado y notifica."""
        for i, item in enumerate(self.widgets_items):
            is_active = (i == index)
            item.active = is_active
            # Actualizamos colores visuales del item
            item.icon_box.background_color = Palette.PRIMARY if is_active else Palette.GRAY_500
            item.label.color = Palette.PRIMARY if is_active else Palette.GRAY_700
            
        if self.on_select:
            self.on_select(index, self.items_labels[index])
        self.events.on_change.emit()

class DrawerLayout(Widget):
    """
    Menú lateral deslizable.
    """
    def __init__(self, x=0, y=0, width=360, height=640, drawer_width=280, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, 
                         background_color=Color(0, 0, 0, 100), **kwargs) # Overlay
        self.drawer_width = drawer_width
        self.is_open = False
        self.visible = False # Oculto por defecto
        
        self.drawer_content = VerticalLayout(
            x=-drawer_width, y=0, width=drawer_width, height=height,
            background_color=Palette.SURFACE, padding=16, spacing=8
        )
        self.add_child(self.drawer_content)

    def open(self):
        self.is_open = True
        self.visible = True
        self.drawer_content.x = 0

    def close(self):
        self.is_open = False
        self.visible = False
        self.drawer_content.x = -self.drawer_width

class AppBarLayout(VerticalLayout):
    """
    Contenedor para la barra de aplicación que soporta elevación y colapso.
    """
    def __init__(self, x=0, y=0, width=360, height=112, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, 
                         spacing=0, padding=0, background_color=Palette.PRIMARY, **kwargs)
        self.shadow_blur = 4

class Breadcrumb(HorizontalLayout):
    """
    Ruta de navegación jerárquica.
    """
    def __init__(self, path=None, x=0, y=0, width=360, height=32, **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, 
                         background_color=Palette.GRAY_100, 
                         spacing=8, padding=8, **kwargs)
        self.path = path or ["Home"]
        self._setup_path()

    def _setup_path(self):
        for i, segment in enumerate(self.path):
            self.add_widget(Label(text=segment, size=14, color=Palette.PRIMARY))
            if i < len(self.path) - 1:
                self.add_widget(Label(text=">", size=14, color=Palette.GRAY_500))
