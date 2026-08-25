# widgets/layouts.py
from .base import Widget

class BoxLayout(Widget):
    def __init__(self, x=0, y=0, width=100, height=100, orientation="vertical", spacing=10, padding=10, children=None, **kwargs):
        """
        Contenedor inteligente que organiza widgets automáticamente.
        
        Args:
            orientation (str): "vertical" u "horizontal".
            spacing (int): Espacio entre widgets.
            padding (int): Margen interno del contenedor.
            children (list): Lista opcional de widgets para inicialización rápida.
            **kwargs: Parámetros adicionales como background_color o id.
        """
        # Inicializamos la clase base (Widget)
        # Esto permite pasar background_color, id, etc., a través de kwargs
        super().__init__(x, y, width, height, children=children, **kwargs)
        
        self.orientation = orientation
        self.spacing = spacing
        self.padding = padding

    def add_widget(self, widget):
        """
        Añade un widget hijo de forma dinámica y actualiza la organización.
        """
        self.add_child(widget)
        self.reposition_children()

    def reposition_children(self):
        """
        Calcula y asigna las coordenadas x, y de cada hijo basándose en 
        la orientación y el espaciado definido.
        """
        if not self.children:
            return

        current_x = self.padding
        current_y = self.padding

        for child in self.children:
            # Asignar posición relativa al layout
            child.x = current_x
            child.y = current_y

            if self.orientation == "vertical":
                # Ajustar ancho del hijo al ancho del layout menos padding
                child.width = self.width - (self.padding * 2)
                # El siguiente widget se posiciona debajo
                current_y += child.height + self.spacing
            else:
                # Ajustar alto del hijo al alto del layout menos padding
                child.height = self.height - (self.padding * 2)
                # El siguiente widget se posiciona a la derecha
                current_x += child.width + self.spacing

    def draw(self, canvas):
        """
        Asegura que los hijos estén alineados antes de renderizar.
        """
        # Forzar reposicionamiento por si el tamaño del layout o de los hijos cambió
        self.reposition_children()
        # Llamar al método draw de Widget para pintar fondo e hijos
        super().draw(canvas)

class VerticalLayout(BoxLayout):
    def __init__(self, **kwargs):
        """Layout preconfigurado para organización de arriba hacia abajo."""
        super().__init__(orientation="vertical", **kwargs)

class HorizontalLayout(BoxLayout):
    def __init__(self, **kwargs):
        """Layout preconfigurado para organización de izquierda a derecha."""
        super().__init__(orientation="horizontal", **kwargs)

class LinearLayout(BoxLayout):
    """Alias para BoxLayout, siguiendo la nomenclatura de Android."""
    pass

class ConstraintLayout(Widget):
    def __init__(self, **kwargs):
        """Layout basado en restricciones entre widgets."""
        super().__init__(**kwargs)
        self.constraints = {}

class RelativeLayout(Widget):
    def __init__(self, **kwargs):
        """Layout que posiciona hijos relativamente a otros o al padre."""
        super().__init__(**kwargs)

class FrameLayout(Widget):
    def __init__(self, **kwargs):
        """Layout diseñado para bloquear un área en pantalla para un solo widget."""
        super().__init__(**kwargs)

class TableLayout(Widget):
    def __init__(self, **kwargs):
        """Layout que organiza widgets en filas y columnas."""
        super().__init__(**kwargs)
        self.rows = []

class GridLayout(Widget):
    def __init__(self, columns=4, spacing=8, padding=12, **kwargs):
        """Layout que organiza widgets en una cuadrícula automática."""
        super().__init__(**kwargs)
        self.columns = columns
        self.spacing = spacing
        self.padding = padding

    def add_widget(self, widget):
        self.add_child(widget)
        self._rebalance()

    def _rebalance(self):
        if not self.children: return
        
        available_w = self.width - (self.padding * 2)
        col_w = (available_w - (self.spacing * (self.columns - 1))) // self.columns
        
        # Asumimos celdas cuadradas o altura fija basada en el primer hijo si no se especifica
        row_h = col_w # Por defecto cuadrada
        
        for i, child in enumerate(self.children):
            row = i // self.columns
            col = i % self.columns
            
            child.width = col_w
            # Si el hijo tiene altura predefinida la usamos, si no, lo hacemos cuadrado
            if child.height == 100: # 100 es el default de Widget
                child.height = col_w
            
            child.x = self.padding + col * (col_w + self.spacing)
            child.y = self.padding + row * (child.height + self.spacing)

    def draw(self, canvas):
        self._rebalance()
        super().draw(canvas)

class CoordinatorLayout(Widget):
    def __init__(self, **kwargs):
        """Layout que facilita interacciones complejas entre sus hijos."""
        super().__init__(**kwargs)