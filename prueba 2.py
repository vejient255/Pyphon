# main.py
from core.app import MobileApp
from core.navigator import Screen
from core.form_validator import FormValidator
from core.i18n import t
from renderer.colors import Palette, Color
from renderer.effects import GlassPanel, DynamicShadow
from widgets import (
    Button, Label, TextInput, Card, VerticalLayout, HorizontalLayout,
    StatusBar, BottomNavigationView, Icon, IconButton, FAB, Snackbar,
    ScrollView, SkeletonScreen, ResponsiveLayout, Divider
)
import os

class LoginScreen(Screen):
    """Pantalla de Inicio de Sesión con Validación de Formulario."""
    def build(self):
        self.name = "Login"
        
        # Animación Shimmer al entrar
        skeleton = SkeletonScreen(pattern="default", width=360, height=800)
        self.add(skeleton)
        skeleton.start()

        # Layout Principal
        root = VerticalLayout(width=360, height=800, padding=24, spacing=16)
        root.background_color = Palette.BACKGROUND
        
        # Header con i18n
        header = VerticalLayout(width=312, height=100, spacing=4)
        header.add_widget(Label(text=t("login.title"), size=32, color=Palette.PRIMARY))
        header.add_widget(Label(text=t("login.subtitle"), size=14, color=Palette.GRAY_700))
        root.add_widget(header)

        # Formulario
        self.form = FormValidator()
        
        # Campos de entrada
        user_input = TextInput(placeholder=t("login.user"), width=312)
        email_input = TextInput(placeholder=t("login.email"), width=312)
        pass_input = TextInput(placeholder=t("login.pass"), width=312)
        
        self.form.add_field("user", user_input, [("required",), ("min_length", 3)])
        self.form.add_field("email", email_input, [("required",), ("email",)])
        self.form.add_field("password", pass_input, [("required",), ("min_length", 6)])
        
        root.add_widget(user_input)
        root.add_widget(email_input)
        root.add_widget(pass_input)

        # Botón de Registro con animación
        btn_submit = Button(text=t("login.submit"), width=312, height=56)
        
        def on_submit():
            btn_submit.haptic()  # Micro-feedback táctil
            if self.form.validate():
                # Navegar a Home si es válido
                app = MobileApp.INSTANCE
                app.push_screen(HomeScreen())
                Snackbar(text="¡Cuenta creada con éxito!").show()
            else:
                Snackbar(text="Revisa los errores en el formulario").show()

        btn_submit.events.on_click.connect(on_submit)
        root.add_widget(btn_submit)

        # Botón para cambiar idioma
        btn_lang = IconButton(icon="translate", size=48)
        btn_lang.events.on_click.connect(lambda: self.toggle_lang())
        root.add_widget(btn_lang)

        self.add(root)

    def toggle_lang(self):
        app = MobileApp.INSTANCE
        new_lang = "en" if app.i18n.current_language == "es" else "es"
        app.i18n.set_language(new_lang)
        # Recargar pantalla actual para ver cambios i18n
        app.navigator.replace(LoginScreen(), transition="fade")

class HomeScreen(Screen):
    """Pantalla Principal con Glassmorphism y Responsive Layout."""
    def build(self):
        self.name = "Home"
        
        root = VerticalLayout(width=360, height=800, padding=0, spacing=0)
        root.background_color = Palette.BACKGROUND
        
        # Barra Superior de Cristal (Glassmorphism)
        top_bar = VerticalLayout(width=360, height=80, padding=16)
        self.glass = GlassPanel()
        
        # Encapsulamos el dibujo del glass en el draw de la barra
        original_draw = top_bar.draw
        def glass_draw(canvas):
            self.glass.draw(canvas, top_bar.x, top_bar.y, top_bar.width, top_bar.height)
            original_draw(canvas)
        top_bar.draw = glass_draw
        
        title_row = HorizontalLayout(width=328, height=48, spacing=12)
        title_row.add_widget(IconButton(icon="menu", size=40))
        title_row.add_widget(Label(text=t("app.title"), size=20, color=Palette.PRIMARY))
        top_bar.add_widget(title_row)
        root.add_widget(top_bar)

        # Área de Contenido con Scroll
        scroll = ScrollView(width=360, height=648)
        content = ResponsiveLayout(width=360, padding=16, spacing=16)
        
        # Añadir varias tarjetas responsivas
        for i in range(6):
            card = Card(width=160, height=180, elevation=4)
            card.add_widget(Label(text=f"Elemento {i+1}", size=16))
            card.add_widget(Divider())
            card.add_widget(Label(text="Contenido premium con sombras dinámicas", size=12))
            content.add_item(card)
        
        scroll.add_widget(content)
        root.add_widget(scroll)

        # FAB (Floating Action Button)
        fab = FAB(icon="add", x=280, y=600)
        fab.events.on_click.connect(lambda: Snackbar(text="Añadir nuevo elemento").show())
        
        # Barra de Navegación Inferior
        nav = BottomNavigationView(width=360, items=[t("nav.home"), t("nav.explore"), t("nav.profile")])
        root.add_widget(nav)
        
        self.add(root)
        self.add(fab)

def main():
    # 1. Init App
    app = MobileApp(titulo="PyPhonOS Ultra Demo", ancho=360, alto=800)
    
    # 2. Configurar i18n
    locales_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")
    if os.path.exists(locales_dir):
        app.i18n.load_directory(locales_dir)
    else:
        # Fallback manual si no lee disco
        app.i18n.add_translations("es", {"app": {"title": "PyPhonOS"}, "login": {"title": "Entrar"}})

    # 3. Configurar Hot-Reload de Tema (opcional)
    theme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme.json")
    if os.path.exists(theme_file):
        app.theme.enable_hot_reload(theme_file)

    # 4. Lanzar con la primera pantalla
    app.push_screen(LoginScreen())
    app.run()

if __name__ == "__main__":
    main()