"""
Interza - Reproductor de Música con Estilo Neumórfico
Demostración del sistema neumórfico de PyPhonOS
"""
from core.app import App
from widgets.base import Widget
from widgets.advanced import (
    NeumorphicWidget, 
    NeumorphicButton, 
    NeumorphicContainer,
    GlassmorphismPanel
)
from widgets.label import Label
from renderer.colors import Color, Palette
from renderer.lighting import NEUMORPHIC_DEFAULT


class MusicPlayerApp(App):
    def __init__(self):
        super().__init__("Interza", width=360, height=640)
        self.is_playing = False
        self.current_time = 0
        self.total_time = 225  # 3:45 en segundos
        
    def build(self):
        # Fondo principal con color neumórfico base
        root = NeumorphicContainer(
            x=0, y=0, 
            width=360, height=640,
            elevation=0.5,
            border_radius=0
        )
        
        # Título
        title = Label(
            text="Reproductor Musical",
            x=80, y=40,
            size=18,
            color=Color(51, 51, 51, 255)
        )
        root.add_child(title)
        
        # Carátula del álbum (círculo neumórfico)
        cover = NeumorphicWidget(
            x=80, y=90,
            width=200, height=200,
            border_radius=100,
            elevation=1.5
        )
        root.add_child(cover)
        
        # Círculo interior para simular disco
        disc = Widget(
            x=100, y=110,
            width=160, height=160,
            background_color=Color(52, 152, 219, 255),
            border_radius=80
        )
        cover.add_child(disc)
        
        # Información de la canción
        song_title = Label(
            text="Nombre de la Canción",
            x=70, y=320,
            size=16,
            color=Color(51, 51, 51, 255)
        )
        root.add_child(song_title)
        
        artist = Label(
            text="Artista",
            x=130, y=345,
            size=14,
            color=Color(100, 100, 100, 255)
        )
        root.add_child(artist)
        
        # Barra de progreso (contenedor hundido)
        progress_bg = NeumorphicWidget(
            x=40, y=380,
            width=280, height=12,
            border_radius=6,
            elevation=0.6
        )
        root.add_child(progress_bg)
        
        # Barra de progreso actual
        self.progress_bar = Widget(
            x=48, y=386,
            width=100, height=6,
            background_color=Color(52, 152, 219, 255),
            border_radius=3
        )
        root.add_child(self.progress_bar)
        
        # Tiempo
        current_time_label = Label(
            text="0:00",
            x=40, y=400,
            size=11,
            color=Color(100, 100, 100, 255)
        )
        root.add_child(current_time_label)
        
        total_time_label = Label(
            text="3:45",
            x=300, y=400,
            size=11,
            color=Color(100, 100, 100, 255)
        )
        root.add_child(total_time_label)
        
        # Controles de reproducción
        # Botón anterior
        btn_prev = NeumorphicButton(
            text="◄◄",
            x=60, y=450,
            width=60, height=60,
            border_radius=30,
            elevation=1.2
        )
        root.add_child(btn_prev)
        
        # Botón play/pause
        self.play_btn = NeumorphicButton(
            text="▶",
            x=150, y=440,
            width=80, height=80,
            border_radius=40,
            elevation=1.5,
            on_click=self.toggle_play
        )
        root.add_child(self.play_btn)
        
        # Botón siguiente
        btn_next = NeumorphicButton(
            text="►►",
            x=260, y=450,
            width=60, height=60,
            border_radius=30,
            elevation=1.2
        )
        root.add_child(btn_next)
        
        # Control de volumen
        volume_label = Label(
            text="Volumen",
            x=130, y=540,
            size=13,
            color=Color(80, 80, 80, 255)
        )
        root.add_child(volume_label)
        
        # Slider de volumen (simulado con widget neumórfico)
        volume_slider = NeumorphicWidget(
            x=60, y=565,
            width=240, height=10,
            border_radius=5,
            elevation=0.6
        )
        root.add_child(volume_slider)
        
        # Indicador de volumen
        volume_indicator = Widget(
            x=60, y=565,
            width=168, height=10,
            background_color=Color(52, 152, 219, 255),
            border_radius=5
        )
        root.add_child(volume_indicator)
        
        return root
    
    def toggle_play(self):
        """Cambia entre play y pause"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.text = "❚❚"
        else:
            self.play_btn.text = "▶"
        print(f"Reproducción: {'Iniciada' if self.is_playing else 'Pausada'}")


if __name__ == "__main__":
    app = MusicPlayerApp()
    app.run()
