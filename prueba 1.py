# calculator.py
# Ejemplo de Aplicación: Calculadora Material Design 3 con PyPhonOS
# Demuestra GridLayout, Glassmorphism, Haptic Feedback y ContrastEngine.

from core.app import MobileApp
from core.navigator import Screen
from renderer.colors import Palette, Color
from renderer.effects import GlassPanel, ContrastEngine
from widgets import (
    Button, Label, Card, VerticalLayout, GridLayout, 
    StatusBar, IconButton, Snackbar
)

class CalculatorScreen(Screen):
    def build(self):
        self.name = "Calculadora"
        self.expr = ""
        
        # --- Root Layout ---
        root = VerticalLayout(width=360, height=800, padding=0, spacing=0)
        root.background_color = Palette.BACKGROUND
        
        # --- 1. Display Area (Glassmorphism) ---
        display_container = VerticalLayout(width=360, height=260, padding=24)
        
        # Efecto de cristal para el display
        self.glass = GlassPanel(blur_intensity=0.8)
        
        # Texto del display
        self.lbl_result = Label(text="0", size=64, color=Palette.PRIMARY, align="right")
        self.lbl_expr = Label(text="", size=18, color=Palette.GRAY_700, align="right")
        
        # Sobreescribir draw para poner el fondo de cristal
        def draw_display(canvas):
            self.glass.draw(canvas, 0, 0, 360, 260, radius=0)
            # Dibujar textos
            self.lbl_expr.x = 24
            self.lbl_expr.y = 80
            self.lbl_expr.width = 312
            self.lbl_expr.draw(canvas)
            
            self.lbl_result.x = 24
            self.lbl_result.y = 120
            self.lbl_result.width = 312
            self.lbl_result.draw(canvas)

        display_container.draw = draw_display
        root.add_widget(display_container)
        
        # --- 2. Teclado (GridLayout) ---
        keypad = GridLayout(columns=4, spacing=12, padding=16, width=360, height=540)
        
        # Definición de botones: (texto, tipo)
        # Tipos: 'num', 'op', 'action'
        buttons = [
            ('C', 'action'), ('(', 'op'), (')', 'op'), ('/', 'op'),
            ('7', 'num'),    ('8', 'num'), ('9', 'num'), ('*', 'op'),
            ('4', 'num'),    ('5', 'num'), ('6', 'num'), ('-', 'op'),
            ('1', 'num'),    ('2', 'num'), ('3', 'num'), ('+', 'op'),
            ('0', 'num'),    ('.', 'num'), ('DEL', 'action'), ('=', 'submit')
        ]
        
        for text, btype in buttons:
            btn = Button(text=text, width=70, height=70, id=f"btn_{text}")
            btn.border_radius = 35 # Botones redondos estilo Android 12+
            
            # Colores según tipo
            if btype == 'num':
                btn.background_color = Palette.SURFACE_V
                btn.text_color = Palette.BLACK
            elif btype == 'op':
                btn.background_color = Palette.PRIMARY_CONTAINER
                btn.text_color = Palette.ON_PRIMARY_CONTAINER
            elif btype == 'submit':
                btn.background_color = Palette.PRIMARY
                btn.text_color = Palette.ON_PRIMARY
            else: # action (C, DEL)
                btn.background_color = Color(255, 180, 180) # Soft red
                btn.text_color = Color(100, 0, 0)

            # Lógica
            btn.events.on_click.connect(lambda t=text: self.on_key(t))
            keypad.add_widget(btn)

        root.add_widget(keypad)
        self.add(root)

    def on_key(self, key):
        # Micro-feedback táctil vía ID
        btn_widget = self.find_by_id(f"btn_{key}")
        if btn_widget:
            MobileApp.INSTANCE.anim.pulse(btn_widget, scale_factor=0.92)
        
        if key == 'C':
            self.expr = ""
            self.lbl_result.text = "0"
            self.lbl_expr.text = ""
        elif key == 'DEL':
            self.expr = self.expr[:-1]
            self.lbl_expr.text = self.expr
        elif key == '=':
            try:
                # Limpieza básica para eval (seguridad mínima en modo demo)
                safe_expr = self.expr.replace('×', '*').replace('÷', '/')
                result = eval(safe_expr)
                self.lbl_result.text = str(result)
                self.expr = str(result)
            except:
                self.lbl_result.text = "Error"
                self.expr = ""
        else:
            if self.lbl_result.text != "0" and len(self.expr) == 0:
                 self.expr = ""
            self.expr += key
            self.lbl_expr.text = self.expr

def run_calculator():
    app = MobileApp(titulo="PyPhon Calc", ancho=360, alto=800)
    app.push_screen(CalculatorScreen())
    app.run()

if __name__ == "__main__":
    run_calculator()
