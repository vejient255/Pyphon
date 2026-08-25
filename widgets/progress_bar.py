# widgets/progress_bar.py
import time
from .base import Widget
from renderer.colors import Palette, Color

class ProgressBar(Widget):
    def __init__(self, progress=0, indeterminate=False, x=0, y=0, width=200, height=4, id=None):
        super().__init__(x, y, width, height, id)
        self.progress = progress # 0.0 to 1.0
        self.indeterminate = indeterminate
        self.start_time = time.time()
        
        # Estilo Material
        self.track_color = Palette.GRAY_300
        self.progress_color = Palette.PRIMARY

    def draw(self, canvas):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        
        # Dibujar track
        canvas.draw_rect(abs_x, abs_y, self.width, self.height, self.track_color)
        
        if self.indeterminate:
            # Animación simple para modo indeterminado
            elapsed = (time.time() - self.start_time) % 2.0
            pos = (elapsed / 2.0) * self.width
            bar_w = self.width // 3
            
            # Dibujar barra que se mueve
            draw_x = abs_x + pos
            if draw_x + bar_w > abs_x + self.width:
                # Parte que sale por la derecha reaparece por la izquierda
                remaining = (draw_x + bar_w) - (abs_x + self.width)
                canvas.draw_rect(abs_x, abs_y, remaining, self.height, self.progress_color)
                canvas.draw_rect(draw_x, abs_y, (abs_x + self.width) - draw_x, self.height, self.progress_color)
            else:
                canvas.draw_rect(draw_x, abs_y, bar_w, self.height, self.progress_color)
        else:
            # Dibujar progreso determinado
            current_w = int(self.progress * self.width)
            canvas.draw_rect(abs_x, abs_y, current_w, self.height, self.progress_color)
