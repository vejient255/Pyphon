# core/window.py
import sdl2
import sdl2.ext
import ctypes

class NativeWindow:
    def __init__(self, ancho, alto, titulo):
        """
        Inicializa una ventana con escalado de alta densidad forzado.
        Optimizado para eliminar el aliasing (píxeles serruchados).
        IMPORTANTE: Las hints de calidad ya se establecen en app.py ANTES de crear esta ventana.
        """
        # Inicializar los subsistemas de SDL2
        sdl2.ext.init()
        
        self.ancho = ancho
        self.alto = alto
        self.corriendo = True
        self.ultimo_clic = None 
        
        # --- VENTANA CON SOPORTE HiDPI ---
        # ALLOW_HIGHDPI es CRÍTICO: permite que la ventana use resolución nativa del monitor
        flags = (
            sdl2.SDL_WINDOW_SHOWN | 
            sdl2.SDL_WINDOW_RESIZABLE | 
            sdl2.SDL_WINDOW_ALLOW_HIGHDPI
        )
        
        self.window = sdl2.ext.Window(
            titulo, 
            size=(self.ancho, self.alto), 
            flags=flags
        )
        self.window.show()
        
        # --- RENDERER CON ACELERACIÓN GPU ---
        renderer_flags = (
            sdl2.SDL_RENDERER_ACCELERATED | 
            sdl2.SDL_RENDERER_PRESENTVSYNC |
            sdl2.SDL_RENDERER_TARGETTEXTURE
        )
        
        self.renderer = sdl2.ext.Renderer(
            self.window, 
            flags=renderer_flags
        )
        
        # NOTA: El tamaño lógico se establece en app.py después de detectar DPI
        # No lo sobrescribimos aquí para evitar conflictos
        
        # Obtenemos el ID de la ventana
        self.window_id = sdl2.SDL_GetWindowID(self.window.window)
        
        # Limpieza completa de variables legacy de Windows para evitar caídas en Android
        self.hwnd = None
        self.hdc = None

    def procesar_mensajes(self):
        """Procesa eventos de entrada del sistema."""
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.corriendo = False
                break
            
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                if event.button.windowID == self.window_id:
                    # Captura de coordenadas precisas
                    x = event.button.x
                    y = event.button.y
                    self.ultimo_clic = (x, y)
            
            elif event.type == sdl2.SDL_WINDOWEVENT:
                if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                    self.ancho = event.window.data1
                    self.alto = event.window.data2

    def presentar(self):
        """Vuelca el buffer de la GPU a la pantalla física."""
        self.renderer.present()

    def cerrar(self):
        """Libera recursos y cierra SDL2."""
        self.renderer.destroy()
        self.window.close()
        sdl2.ext.quit()