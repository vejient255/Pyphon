# interza.py - Reproductor de Música con estilo Neumorfismo usando PyPhonOS
from core.app import MobileApp
from widgets.base import Widget
from widgets.button import Button
from widgets.label import Label
from renderer.colors import Color, Palette
from renderer.canvas import Canvas
import math

class NeumorphicButton(Widget):
    """Botón con estilo Neumorfismo (sombras claras y oscuras simultáneas)"""
    
    def __init__(self, x, y, width, height, text="", on_click=None, circular=False, **kwargs):
        super().__init__(x, y, width, height, on_click=on_click, **kwargs)
        self.text = text
        self.circular = circular
        self.is_pressed = False
        
        # Colores Neumórficos
        self.neumo_bg = Color(224, 229, 236)  # #E0E5EC
        self.light_shadow = Color(255, 255, 255)  # Blanco
        self.dark_shadow = Color(163, 177, 198)  # #A3B1C6
        self.icon_color = Color(51, 51, 51)  # #333333
        
        # Sin sombra por defecto (usaremos nuestro propio sistema)
        self.shadow_blur = 0
    
    def draw(self, canvas):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Determinar offset basado en estado presionado
        offset = 3 if self.is_pressed else 0
        
        # Dibujar fondo base
        if self.circular:
            # Botón circular
            center_x = abs_x + self.width // 2
            center_y = abs_y + self.height // 2
            radius = min(self.width, self.height) // 2
            
            # Sombra clara (superior izquierda)
            for i in range(3):
                canvas.draw_circle(
                    center_x - i, center_y - i, radius,
                    self.light_shadow, alpha=80
                )
            
            # Sombra oscura (inferior derecha)
            for i in range(3):
                canvas.draw_circle(
                    center_x + i, center_y + i, radius,
                    self.dark_shadow, alpha=60
                )
            
            # Botón principal
            canvas.draw_circle(
                center_x, center_y, radius,
                self.neumo_bg
            )
            
            # Dibujar icono
            self._draw_icon(canvas, center_x, center_y, offset)
        else:
            # Botón rectangular con bordes redondeados
            r = 15
            
            # Sombra clara
            canvas.draw_rounded_rect(
                abs_x - 2, abs_y - 2, self.width, self.height, r,
                self.light_shadow, alpha=80
            )
            
            # Sombra oscura
            canvas.draw_rounded_rect(
                abs_x + 2, abs_y + 2, self.width, self.height, r,
                self.dark_shadow, alpha=60
            )
            
            # Botón principal
            canvas.draw_rounded_rect(
                abs_x + offset, abs_y + offset, 
                self.width - offset*2, self.height - offset*2, r,
                self.neumo_bg
            )
            
            # Dibujar texto
            if self.text:
                canvas.draw_text(
                    self.text,
                    abs_x + self.width//2 - 20,
                    abs_y + self.height//2 - 10,
                    self.icon_color,
                    size=16
                )
    
    def _draw_icon(self, canvas, cx, cy, offset):
        """Dibuja iconos de reproducción"""
        if self.text == "play":
            # Triángulo play
            points = [
                (cx - 8 + offset//2, cy - 10 + offset//2),
                (cx - 8 + offset//2, cy + 10 + offset//2),
                (cx + 12 + offset//2, cy + offset//2)
            ]
            self._draw_triangle(canvas, points, self.icon_color)
        elif self.text == "pause":
            # Dos rectángulos pause
            canvas.draw_rect(cx - 6 + offset//2, cy - 8 + offset//2, 4, 16, self.icon_color)
            canvas.draw_rect(cx + 2 + offset//2, cy - 8 + offset//2, 4, 16, self.icon_color)
        elif self.text == "prev":
            # Triángulo hacia atrás + línea
            points = [
                (cx + 8 + offset//2, cy - 10 + offset//2),
                (cx + 8 + offset//2, cy + 10 + offset//2),
                (cx - 8 + offset//2, cy + offset//2)
            ]
            self._draw_triangle(canvas, points, self.icon_color)
            canvas.draw_rect(cx + 10 + offset//2, cy - 10 + offset//2, 3, 20, self.icon_color)
        elif self.text == "next":
            # Triángulo hacia adelante + línea
            points = [
                (cx - 8 + offset//2, cy - 10 + offset//2),
                (cx - 8 + offset//2, cy + 10 + offset//2),
                (cx + 8 + offset//2, cy + offset//2)
            ]
            self._draw_triangle(canvas, points, self.icon_color)
            canvas.draw_rect(cx - 13 + offset//2, cy - 10 + offset//2, 3, 20, self.icon_color)
    
    def _draw_triangle(self, canvas, points, color):
        """Dibuja un triángulo simple"""
        # Usamos draw_rect pequeños para simular líneas
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i+1) % len(points)]
            # Línea simple entre dos puntos
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                angle = math.atan2(dy, dx)
                for j in range(int(dist)):
                    px = p1[0] + math.cos(angle) * j
                    py = p1[1] + math.sin(angle) * j
                    canvas.write_pixel(int(px), int(py), color)
    
    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
        
        ex, ey = event.get('x', 0), event.get('y', 0)
        etype = event.get('type')
        inside = self.is_point_inside(ex, ey)
        
        if etype == "touch_down" and inside:
            self.is_pressed = True
            return True
        elif etype == "touch_up":
            if self.is_pressed and inside:
                self.is_pressed = False
                self.events.on_click.emit()
                return True
            self.is_pressed = False
        
        return False


class NeumorphicPanel(Widget):
    """Panel con efecto Neumórfico para contenedores"""
    
    def __init__(self, x, y, width, height, border_radius=20, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self.border_radius = border_radius
        self.neumo_bg = Color(224, 229, 236)
        self.light_shadow = Color(255, 255, 255)
        self.dark_shadow = Color(163, 177, 198)
        self.background_color = self.neumo_bg
    
    def draw(self, canvas):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        r = self.border_radius
        
        # Sombra clara (superior izquierda)
        canvas.draw_rounded_rect(
            abs_x - 3, abs_y - 3, self.width, self.height, r,
            self.light_shadow, alpha=70
        )
        
        # Sombra oscura (inferior derecha)
        canvas.draw_rounded_rect(
            abs_x + 3, abs_y + 3, self.width, self.height, r,
            self.dark_shadow, alpha=50
        )
        
        # Panel principal
        canvas.draw_rounded_rect(
            abs_x, abs_y, self.width, self.height, r,
            self.neumo_bg
        )
        
        # Dibujar hijos
        for child in self.children:
            child.draw(canvas)


class AlbumCover(Widget):
    """Carátula de álbum circular con efecto Neumórfico"""
    
    def __init__(self, x, y, size, **kwargs):
        super().__init__(x, y, size, size, **kwargs)
        self.size = size
        self.neumo_bg = Color(224, 229, 236)
        self.light_shadow = Color(255, 255, 255)
        self.dark_shadow = Color(163, 177, 198)
        self.album_color = Color(52, 152, 219)  # Azul
    
    def draw(self, canvas):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        center_x = abs_x + self.size // 2
        center_y = abs_y + self.size // 2
        radius = self.size // 2
        
        # Sombra clara exterior
        for i in range(4):
            canvas.draw_circle(
                center_x - i, center_y - i, radius,
                self.light_shadow, alpha=60
            )
        
        # Sombra oscura exterior
        for i in range(4):
            canvas.draw_circle(
                center_x + i, center_y + i, radius,
                self.dark_shadow, alpha=50
            )
        
        # Círculo principal (marco)
        canvas.draw_circle(center_x, center_y, radius, self.neumo_bg)
        
        # Círculo interior hundido (para la imagen)
        inner_radius = radius - 10
        canvas.draw_circle(center_x, center_y, inner_radius, Color(200, 210, 220))
        
        # Arte del álbum (círculo de color)
        canvas.draw_circle(center_x, center_y, inner_radius - 5, self.album_color)
        
        # Centro del disco
        canvas.draw_circle(center_x, center_y, 15, self.neumo_bg)
        canvas.draw_circle(center_x, center_y, 8, Color(50, 50, 50))


class MusicPlayerScreen:
    """Pantalla principal del reproductor"""
    
    def __init__(self, app):
        self.app = app
        self.widgets = []
        self.is_playing = False
        self.current_time = 0
        self.total_time = 225  # 3:45 en segundos
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Fondo general
        bg_color = Color(224, 229, 236)
        
        # Título
        title = Label(
            text="Reproductor Musical",
            x=80, y=40,
            width=200, height=30,
            size=18,
            color=Color(51, 51, 51)
        )
        self.widgets.append(title)
        
        # Carátula del álbum
        self.album_cover = AlbumCover(x=80, y=100, size=200)
        self.widgets.append(self.album_cover)
        
        # Información de la canción
        song_title = Label(
            text="Nombre de la Canción",
            x=90, y=320,
            width=180, height=30,
            size=16,
            color=Color(51, 51, 51)
        )
        self.widgets.append(song_title)
        
        artist_name = Label(
            text="Artista",
            x=130, y=350,
            width=100, height=25,
            size=14,
            color=Color(100, 100, 100)
        )
        self.widgets.append(artist_name)
        
        # Barra de progreso (panel hundido)
        progress_panel = NeumorphicPanel(x=40, y=390, width=280, height=20, border_radius=10)
        self.widgets.append(progress_panel)
        
        # Barra de progreso interna
        self.progress_bar = Widget(48, 395, 140, 10)
        self.progress_bar.background_color = Color(52, 152, 219)
        self.progress_bar.border_radius = 5
        self.widgets.append(self.progress_bar)
        
        # Tiempos
        current_time_label = Label(
            text="0:00",
            x=40, y=420,
            width=50, height=20,
            size=12,
            color=Color(100, 100, 100)
        )
        self.widgets.append(current_time_label)
        
        total_time_label = Label(
            text="3:45",
            x=270, y=420,
            width=50, height=20,
            size=12,
            color=Color(100, 100, 100)
        )
        self.widgets.append(total_time_label)
        
        # Controles de reproducción
        # Botón anterior
        self.prev_btn = NeumorphicButton(
            x=60, y=470, width=50, height=50,
            text="prev", circular=True,
            on_click=self.previous_track
        )
        self.widgets.append(self.prev_btn)
        
        # Botón play/pause (más grande)
        self.play_btn = NeumorphicButton(
            x=155, y=460, width=70, height=70,
            text="play", circular=True,
            on_click=self.toggle_play
        )
        self.widgets.append(self.play_btn)
        
        # Botón siguiente
        self.next_btn = NeumorphicButton(
            x=270, y=470, width=50, height=50,
            text="next", circular=True,
            on_click=self.next_track
        )
        self.widgets.append(self.next_btn)
        
        # Control de volumen
        volume_label = Label(
            text="Volumen",
            x=130, y=550,
            width=100, height=25,
            size=14,
            color=Color(51, 51, 51)
        )
        self.widgets.append(volume_label)
        
        # Slider de volumen (simplificado como barra)
        volume_bg = NeumorphicPanel(x=60, y=580, width=240, height=15, border_radius=8)
        self.widgets.append(volume_bg)
        
        self.volume_fill = Widget(68, 584, 170, 7)
        self.volume_fill.background_color = Color(52, 152, 219)
        self.volume_fill.border_radius = 4
        self.widgets.append(self.volume_fill)
    
    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.play_btn.text = "pause" if self.is_playing else "play"
        print(f"Reproducción: {'Iniciada' if self.is_playing else 'Pausada'}")
    
    def previous_track(self):
        print("Pista anterior")
    
    def next_track(self):
        print("Pista siguiente")
    
    def update(self):
        """Actualiza el estado de la pantalla"""
        if self.is_playing:
            self.current_time += 1
            if self.current_time >= self.total_time:
                self.current_time = 0
                self.is_playing = False
                self.play_btn.text = "play"
            
            # Actualizar barra de progreso
            progress_width = int((self.current_time / self.total_time) * 140)
            self.progress_bar.width = progress_width


def main():
    app = MobileApp(titulo="Interza - Reproductor Neumórfico", ancho=360, alto=640)
    
    # Crear pantalla del reproductor
    player_screen = MusicPlayerScreen(app)
    
    # Añadir widgets al app
    for widget in player_screen.widgets:
        app.add_widget(widget)
    
    # Loop de actualización personalizado
    original_render = app._render_frame
    
    def custom_render():
        player_screen.update()
        original_render()
    
    app._render_frame = custom_render
    
    print("Interza - Reproductor de Música con Neumorfismo")
    print("Usa F12 para activar el inspector de widgets")
    
    app.run()


if __name__ == "__main__":
    main()
