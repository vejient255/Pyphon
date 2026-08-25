
from .base import Widget
from .label import Label
from .layouts import HorizontalLayout, VerticalLayout
from .button import Button
from renderer.colors import Palette, Color
import math
import time

class Badge(Label):
    def __init__(self, text="1", **kwargs):
        super().__init__(text=text, **kwargs)
        self.background_color = Palette.ERROR
        self.text_color = Palette.WHITE
        self.border_radius = 10
        self.padding = 4
        self.size = 12

class Chip(HorizontalLayout):
    def __init__(self, text="Chip", icon=None, **kwargs):
        super().__init__(**kwargs)
        self.height = 32
        self.background_color = Palette.GRAY_300
        self.border_radius = 16
        self.padding = 8
        self.spacing = 4
        
        if icon:
            self.add_widget(Label(text=icon, size=14))
        self.add_widget(Label(text=text, size=14, color=Palette.BLACK))

class Divider(Widget):
    def __init__(self, orientation="horizontal", **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.GRAY_300
        if orientation == "horizontal":
            self.height = 1
        else:
            self.width = 1

class Space(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Palette.TRANSPARENT


class ShimmerLayout(Widget):
    """
    Efecto Shimmer animado (ola de luz que pasa sobre el contenido).
    Se usa como placeholder mientras los datos se cargan.

    Uso:
        shimmer = ShimmerLayout(width=300, height=80)
        shimmer.start()
    """
    def __init__(self, shimmer_color=None, base_color=None,
                 speed=1.5, wave_width=80, **kwargs):
        super().__init__(**kwargs)
        self.shimmer_color = shimmer_color or Color(255, 255, 255, 100)
        self.base_color = base_color or Color(230, 225, 238)
        self.background_color = self.base_color
        self.speed = speed               # Ciclos por segundo
        self.wave_width = wave_width     # Ancho de la ola de brillo
        self._running = False
        self._start_time = 0
        self.border_radius = 8

    def start(self):
        self._running = True
        self._start_time = time.time()

    def stop(self):
        self._running = False

    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()

        # Dibujar fondo base
        canvas.draw_rounded_rect(
            abs_x, abs_y, self.width, self.height,
            self.border_radius, self.base_color, alpha=self.base_color.a
        )

        if self._running:
            elapsed = time.time() - self._start_time
            # Posición de la ola: se mueve de izquierda a derecha cíclicamente
            cycle = (elapsed * self.speed) % 1.0
            wave_x = int((self.width + self.wave_width * 2) * cycle - self.wave_width)

            # Dibujar la ola de brillo (gradiente simulado con rectángulos)
            num_slices = self.wave_width
            for i in range(num_slices):
                # Gradiente: 0 → máximo → 0 (triangular)
                t = i / num_slices
                intensity = 1.0 - abs(2.0 * t - 1.0)  # Triángulo
                alpha = int(self.shimmer_color.a * intensity)

                slice_x = abs_x + wave_x + i
                if abs_x <= slice_x < abs_x + self.width:
                    canvas.draw_rect(
                        slice_x, abs_y, 1, self.height,
                        self.shimmer_color, alpha=alpha
                    )

        # Dibujar hijos encima
        for child in self.children:
            child.draw(canvas)


class Placeholder(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Color(230, 225, 238)
        self.border_radius = 4
        
    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()
        canvas.draw_rounded_rect(
            abs_x, abs_y, self.width, self.height,
            self.border_radius, self.background_color,
            alpha=self.background_color.a
        )


class SkeletonScreen(VerticalLayout):
    """
    Pantalla esqueleto con shimmer animado.
    Genera automáticamente placeholders con el efecto de carga.

    Uso:
        skeleton = SkeletonScreen(width=320, height=300, pattern="card")
        skeleton.start()
        # Cuando los datos lleguen:
        skeleton.stop()
    """
    def __init__(self, pattern="default", **kwargs):
        super().__init__(spacing=12, padding=0, **kwargs)
        self._shimmer = ShimmerLayout(
            width=kwargs.get('width', 320),
            height=kwargs.get('height', 300)
        )
        self._pattern = pattern
        self._build_pattern()

    def _build_pattern(self):
        """Genera los placeholders según el patrón seleccionado."""
        w = self.width - 20

        if self._pattern == "card":
            # Avatar + líneas de texto
            row = HorizontalLayout(width=w, height=48, spacing=12, padding=0)
            row.add_widget(Placeholder(width=48, height=48))  # Avatar circular
            col = VerticalLayout(width=w - 60, height=48, spacing=8, padding=0)
            col.add_widget(Placeholder(width=int(w * 0.6), height=16))
            col.add_widget(Placeholder(width=int(w * 0.4), height=12))
            row.add_widget(col)
            self.add_widget(row)
            self.add_widget(Placeholder(width=w, height=120))  # Imagen
            self.add_widget(Placeholder(width=w, height=14))   # Texto
            self.add_widget(Placeholder(width=int(w * 0.7), height=14))

        elif self._pattern == "list":
            for _ in range(5):
                row = HorizontalLayout(width=w, height=56, spacing=12, padding=0)
                row.add_widget(Placeholder(width=40, height=40))
                col = VerticalLayout(width=w - 52, height=40, spacing=6, padding=0)
                col.add_widget(Placeholder(width=int(w * 0.5), height=14))
                col.add_widget(Placeholder(width=int(w * 0.3), height=12))
                row.add_widget(col)
                self.add_widget(row)

        elif self._pattern == "profile":
            self.add_widget(Placeholder(width=80, height=80))   # Avatar grande
            self.add_widget(Placeholder(width=int(w * 0.5), height=20))
            self.add_widget(Placeholder(width=int(w * 0.3), height=14))
            self.add_widget(Space(width=w, height=16))
            self.add_widget(Placeholder(width=w, height=60))
            self.add_widget(Placeholder(width=w, height=60))

        else:  # "default"
            self.add_widget(Placeholder(width=w, height=20))
            self.add_widget(Placeholder(width=int(w * 0.8), height=16))
            self.add_widget(Placeholder(width=w, height=100))
            self.add_widget(Placeholder(width=int(w * 0.6), height=14))
            self.add_widget(Placeholder(width=w, height=14))

    def start(self):
        self._shimmer.width = self.width
        self._shimmer.height = self.height
        self._shimmer.start()

    def stop(self):
        self._shimmer.stop()

    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()

        # Dibujamos el shimmer como capa base
        self._shimmer.x = self.x
        self._shimmer.y = self.y
        self._shimmer.parent = self.parent
        self._shimmer.draw(canvas)

        # Dibujamos los placeholders encima
        super().draw(canvas)


class LottieAnimationView(Widget):
    def draw(self, canvas):
        super().draw(canvas)
        abs_x, abs_y = self.get_absolute_position()
        canvas.draw_text("▶ Anim", abs_x + 4, abs_y + 4, Palette.PRIMARY, size=12)

class CircularProgressIndicator(Widget):
    """Indicador de progreso circular animado."""
    def __init__(self, progress=0.0, indeterminate=False, **kwargs):
        super().__init__(**kwargs)
        self.progress = progress
        self.indeterminate = indeterminate
        self.color = Palette.PRIMARY
        self.track_color = Color(230, 225, 238)
        self.stroke_width = 4
        self._start_time = time.time()
        
    def draw(self, canvas):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()
        cx = abs_x + self.width // 2
        cy = abs_y + self.height // 2
        r = min(self.width, self.height) // 2 - self.stroke_width

        # Track (fondo)
        canvas.draw_circle(cx, cy, r, self.track_color, alpha=self.track_color.a)

        # En modo indeterminado, rotar continuamente
        if self.indeterminate:
            elapsed = (time.time() - self._start_time) % 2.0
            self.progress = (elapsed / 2.0)

        # Indicador (arco simplificado como círculo parcial)
        if self.progress > 0:
            indicator_r = r - self.stroke_width
            canvas.draw_circle(cx, cy, indicator_r, self.color, alpha=self.color.a)

class LoadingButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_loading = False
        self.original_text = self.text
        
    def set_loading(self, loading):
        self.is_loading = loading
        self.text = "⏳ Cargando..." if loading else self.original_text
        self.enabled = not loading

class StateLayout(Widget):
    """
    Layout con múltiples estados: content, loading, error, empty.
    Muestra un widget diferente según el estado actual.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "content"  # "loading", "error", "empty", "content"
        self.content_view = None
        self.loading_view = None
        self.error_view = None
        self.empty_view = None
        
        # Crear vistas por defecto
        self._default_loading = SkeletonScreen(
            width=kwargs.get('width', 300),
            height=kwargs.get('height', 200),
            pattern="default"
        )
        self._default_loading.start()

        self._default_error = Label(text="⚠ Error al cargar", size=16,
                                    color=Palette.ERROR)
        self._default_empty = Label(text="📭 Sin contenido", size=16,
                                    color=Palette.GRAY_500)
        
    def set_state(self, state):
        """Cambia el estado: 'content', 'loading', 'error', 'empty'."""
        self.state = state
        
    def draw(self, canvas):
        if not self.visible:
            return

        view = None
        if self.state == "content" and self.content_view:
            view = self.content_view
        elif self.state == "loading":
            view = self.loading_view or self._default_loading
        elif self.state == "error":
            view = self.error_view or self._default_error
        elif self.state == "empty":
            view = self.empty_view or self._default_empty

        if view:
            view.x = self.x
            view.y = self.y
            view.parent = self.parent
            view.draw(canvas)
