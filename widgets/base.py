# widgets/base.py
import sdl2
from renderer.colors import Palette, Color
from events.handler import EventHandler
from renderer.lighting import LightingEngine

class Widget:
    def __init__(self, x=0, y=0, width=100, height=100, id=None, children=None, background_color=Palette.SURFACE, on_click=None, **kwargs):
        """
        Clase base para todos los componentes.
        Soporta inicialización declarativa de hijos y eventos.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.id = id
        self.hero_tag = kwargs.get("hero_tag", None)  # Para animaciones de elementos compartidos
        
        # Sistema de eventos
        self.events = EventHandler()
        if on_click:
            self.events.on_click.connect(on_click)
        
        # Propiedades de Estado
        self.visible = True
        self.enabled = True
        self.is_focused = False
        self.is_pressed = False  # Nuevo estado para botones
        self.opacity = 1.0  # 0.0 = invisible, 1.0 = opaco
        
        # Estilo Base Moderno
        self.background_color = background_color
        self.border_color = Palette.OUTLINE
        self.border_width = 0
        self.border_radius = 0 # Valor por defecto
        self.shadow_color = Color(0, 0, 0, 0) # Sombra desactivada por defecto
        self.shadow_offset = (0, 0)
        self.shadow_blur = 0
        self.haptic_enabled = True  # Feedback táctil visual
        
        # Propiedades Neumórficas
        self.neumorphic = kwargs.get("neumorphic", False)
        self.elevation = kwargs.get("elevation", 1.0)  # Altura del relieve (0.5 a 3.0)
        self.light_angle = kwargs.get("light_angle", 315)  # Ángulo de luz
        
        # Jerarquía
        self.parent = None
        self.children = []
        
        # Si se pasan hijos en el constructor, los agregamos automáticamente
        if children:
            for child in children:
                self.add_child(child)

    def animate(self, duration=0.3, easing="ease_out", delay=0.0,
                on_complete=None, **props):
        """
        Método de conveniencia para animar propiedades de este widget.
        Ejemplo: widget.animate(y=200, opacity=0, duration=0.5, easing='bounce')
        """
        from core.animation import AnimationManager
        anim = AnimationManager.INSTANCE
        if anim is None:
            # Si no hay AnimationManager activo, aplica el valor directamente
            for prop, val in props.items():
                if hasattr(self, prop):
                    setattr(self, prop, val)
            return
        for prop, to_val in props.items():
            if hasattr(self, prop):
                anim.tween(self, prop, to_val, duration=duration,
                           easing=easing, delay=delay,
                           on_complete=on_complete if prop == list(props)[-1] else None)

    def haptic(self, intensity=0.96):
        """
        Aplica un micro-feedback táctil visual (pulso de escala).
        Simula la sensación de "presionar" un botón real.
        """
        if not self.haptic_enabled:
            return
        from core.animation import AnimationManager
        anim = AnimationManager.INSTANCE
        if anim:
            anim.pulse(self, scale_factor=intensity, duration=0.08)

    def find_by_id(self, widget_id):
        """Busca un widget por ID en toda la jerarquía de hijos."""
        if self.id == widget_id:
            return self
        for child in self.children:
            found = child.find_by_id(widget_id)
            if found:
                return found
        return None

    def add_child(self, child_widget):
        """Añade un widget hijo y establece la relación de parentesco."""
        child_widget.parent = self
        self.children.append(child_widget)

    def get_absolute_position(self):
        """Calcula la posición real sumando las coordenadas de los padres."""
        if self.parent:
            px, py = self.parent.get_absolute_position()
            return (self.x + px, self.y + py)
        return (self.x, self.y)

    def is_point_inside(self, tx, ty):
        """Verifica si un punto (clic/toque) está dentro de los límites."""
        abs_x, abs_y = self.get_absolute_position()
        return (abs_x <= tx <= abs_x + self.width and 
                abs_y <= ty <= abs_y + self.height)

    def draw(self, canvas):
        """Dibuja el widget con soporte para sombras y bordes redondeados."""
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()

        # 1. Dibujar con efecto Neumórfico si está activado
        if self.neumorphic:
            canvas.draw_neumorphic_surface(
                abs_x, abs_y, self.width, self.height,
                self.border_radius,
                self.background_color,
                elevation=self.elevation,
                pressed=self.is_pressed,
                light_angle=self.light_angle
            )
        else:
            # 1. Dibujar Sombra tradicional (si aplica)
            if self.shadow_blur > 0:
                canvas.draw_shadow(
                    abs_x + self.shadow_offset[0], 
                    abs_y + self.shadow_offset[1], 
                    self.width, self.height, 
                    radius=self.shadow_blur, 
                    intensity=self.shadow_color.a
                )

            # 2. Dibujar Fondo (soporta redondeado)
            if self.background_color and self.background_color.a > 0:
                if self.border_radius > 0:
                    canvas.draw_rounded_rect(
                        abs_x, abs_y, self.width, self.height, 
                        self.border_radius, self.background_color, alpha=self.background_color.a
                    )
                else:
                    canvas.draw_rect(abs_x, abs_y, self.width, self.height, self.background_color, alpha=self.background_color.a)

            # 3. Dibujar Borde (si aplica)
            if self.border_width > 0:
                canvas.draw_rounded_rect(
                    abs_x, abs_y, self.width, self.height, 
                    self.border_radius, self.border_color, alpha=60 # Borde muy tenue
                )

        # 4. Dibujar hijos encima
        for child in self.children:
            child.draw(canvas)


    def handle_event(self, event):
        """Propaga el evento a los hijos o lo maneja él mismo."""
        if not self.enabled or not self.visible:
            return False
            
        # Prioridad a los hijos (los que están más al frente)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Manejo de clic básico si el evento tiene x, y
        if hasattr(event, 'x') and hasattr(event, 'y'):
            if self.is_point_inside(event.x, event.y):
                # Actualizar estado is_pressed para widgets neumórficos
                if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    self.is_pressed = True
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    self.is_pressed = False
                
                self.events.on_click.emit()
                return True
        return False