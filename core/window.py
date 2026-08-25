# core/window.py
import sdl2
import sdl2.ext
import ctypes

class NativeWindow:
    def __init__(self, ancho, alto, titulo):
        """
        Inicializa una ventana con tamaño fijo de teléfono (360x640).
        La ventana mantiene exactamente este tamaño físico en pantalla,
        sin escalado, para simular un dispositivo móvil real.
        """
        # Inicializar los subsistemas de SDL2
        sdl2.ext.init()
        
        self.ancho_logico = ancho  # Coordenadas lógicas (360x640)
        self.alto_logico = alto
        
        # Tamaño físico exacto de la ventana (sin escalado)
        self.ancho = ancho
        self.alto = alto
        
        self.corriendo = True
        self.ultimo_clic = None 
        
        # --- VENTANA CON TAMAÑO FIJO DE TELÉFONO (360x640) ---
        # Usamos resolución base de Android para que quepa perfectamente en cualquier monitor
        # Sin ALLOW_HIGHDPI y sin escalado para control total del tamaño
        flags = sdl2.SDL_WINDOW_SHOWN  # Sin RESIZABLE para ventana fija
        
        self.window = sdl2.ext.Window(
            titulo, 
            size=(self.ancho, self.alto),  # Tamaño físico: 360x640
            flags=flags
        )
        self.window.show()
        
        # Forzar tamaño fijo (evitar que usuario redimensione)
        sdl2.SDL_SetWindowMinimumSize(self.window.window, self.ancho, self.alto)
        sdl2.SDL_SetWindowMaximumSize(self.window.window, self.ancho, self.alto)
        
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
        
        # Calidad de escalado suave (bilinear filtering) para evitar pixelación
        sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"1")
        
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