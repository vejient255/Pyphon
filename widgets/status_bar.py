# widgets/status_bar.py
from .base import Widget
from .label import Label
from renderer.colors import Palette, Color
from datetime import datetime

class StatusBar(Widget):
    def __init__(self, width=360):
        """
        Barra de estado superior que muestra la hora y el estado del sistema.
        """
        super().__init__(x=0, y=0, width=width, height=24, background_color=Palette.BACKGROUND)
        self.clock_label = Label(text="00:00", size=14, color=Palette.GRAY_900)
        self.clock_label.x = 16
        self.clock_label.y = 4
        self.add_child(self.clock_label)
        
    def draw(self, canvas):
        # Actualizar la hora en cada frame
        ahora = datetime.now().strftime("%H:%M")
        if self.clock_label.text != ahora:
            self.clock_label.text = ahora
            
        super().draw(canvas)
        
        # Dibujar iconos minimalistas (Batería y Wifi)
        abs_x, abs_y = self.get_absolute_position()
        icon_color = Palette.GRAY_900
        
        # Icono de Batería (Simulado)
        bat_x = abs_x + self.width - 35
        bat_y = abs_y + 6
        # Cuerpo
        canvas.draw_rect(bat_x, bat_y, 20, 10, icon_color, alpha=255)
        # Punta
        canvas.draw_rect(bat_x + 20, bat_y + 3, 2, 4, icon_color, alpha=255)
        # Nivel de carga (simulado al 80%)
        canvas.draw_rect(bat_x + 2, bat_y + 2, 14, 6, Palette.PRIMARY, alpha=255)
        
        # Icono de Wifi (Puntos)
        wifi_x = abs_x + self.width - 60
        for i in range(3):
            h = 4 + (i * 3)
            canvas.draw_rect(wifi_x + (i * 5), bat_y + (10 - h), 3, h, icon_color, alpha=255)
